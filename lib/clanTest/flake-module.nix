{
  lib,
  self,
  config,
  ...
}:
let
  inherit (lib)
    mkForce
    mkIf
    mkOption
    types
    ;

  clanLib = config.flake.clanLib;
in
{
  # A function that returns an extension to runTest
  # TODO: remove this from clanLib, add to legacyPackages, simplify signature
  flake.modules.nixosTest.clanTest =
    {
      config,
      options,
      hostPkgs,
      ...
    }:
    let
      testName = config.name;

      clan-core = self;

      inherit (lib)
        filterAttrs
        hasPrefix
        intersectAttrs
        mapAttrs'
        pathExists
        removePrefix
        throwIf
        ;

      # only relevant if config.clan.test.fromFlake is used
      importFlake =
        flakeDir:
        let
          flakeExpr = import (flakeDir + "/flake.nix");
          inputs = intersectAttrs flakeExpr.inputs clan-core.inputs;
          flake = flakeExpr.outputs (
            inputs
            // {
              self = flake // {
                outPath = flakeDir;
              };
              clan-core = clan-core;
              systems = config.clan.test.systemsFile;
            }
          );
        in
        throwIf (pathExists (
          flakeDir + "/flake.lock"
        )) "Test ${testName} should not have a flake.lock file" flake;

      clanFlakeResult =
        if config.clan.test.fromFlake != null then importFlake config.clan.test.fromFlake else config.clan;

      machineModules' = filterAttrs (
        name: _module: hasPrefix "clan-machine-" name
      ) clanFlakeResult.nixosModules;

      machineModules = mapAttrs' (name: machineModule: {
        name = removePrefix "clan-machine-" name;
        value = machineModule;
      }) machineModules';

      machinesCross = lib.genAttrs [ "aarch64-darwin" "aarch64-linux" "x86_64-linux" ] (
        system:
        lib.mapAttrs (
          _: module:
          lib.nixosSystem {
            inherit system;
            modules = [ module ];
          }
        ) machineModules
      );

      # Import the Nix-based vars execution system
      varsExecutor = import ./vars-executor.nix { inherit lib; };

      vars-check = hostPkgs.runCommand "vars-check-${testName}" { } (
        varsExecutor.generateExecutionScript hostPkgs config.nodes
      );

      # Age test key for encrypting generated secrets
      testAgePublicKey = "age1cxmh3ej2lyj3d5yd50t6fx8gyddyrpp9kuhv470wg7avaqau858s7hpe3n";

      # Use clanInternals.machines to get generators WITHOUT the test defaults block.
      # This avoids infinite recursion: config.nodes includes defaults which sets
      # settings.directory → mergedTestDir → config.nodes → cycle.
      # clanInternals.machines are evaluated independently from the clan module,
      # not from config.nodes, so there's no cycle.
      # Build generators for the evaluating system: the vars IFD must build
      # locally, so pinning a single arch breaks checks on other hosts. Generator
      # output is platform-independent text (keys, configs).
      hostSystem = hostPkgs.stdenv.hostPlatform.system;

      clanNodes = lib.mapAttrs (
        _name: system: system.config
      ) clanFlakeResult.clanInternals.machines.${hostSystem};

      # Pkgs for IFD derivations — the evaluating system so the derivation can
      # build locally without requiring a remote builder or emulation.
      ifdPkgs = clan-core.inputs.nixpkgs.legacyPackages.${hostSystem};

      # Run generators and produce age-encrypted secrets + plaintext vars
      generatedVarsDir = varsExecutor.generateVarsDerivation ifdPkgs clanNodes testAgePublicKey;

      # Merge the test's base directory with generated vars/secrets
      mergedTestDir = ifdPkgs.runCommand "merged-test-dir-${testName}" { } ''
        cp -r ${config.clan.directory} $out
        chmod -R +w $out
        rm -rf $out/sops $out/vars $out/secrets
        cp -r ${generatedVarsDir}/vars $out/vars
        cp -r ${generatedVarsDir}/secrets $out/secrets
      '';

      # the test's flake.nix with locked clan-core input
      flakeForSandbox =
        let
          clan-core-flake = self.filter {
            name = "clan-core-flake-filtered";
            include = [
              "flake.nix"
              "flake.lock"
              "checks"
              "clanServices"
              "darwinModules"
              "flakeModules"
              "lib"
              "modules"
              "nixosModules"
            ];
          };
        in
        hostPkgs.runCommand "offline-flake-for-test-${config.name}"
          {
            nativeBuildInputs = [ hostPkgs.nix ];
          }
          ''
            cp -r ${config.clan.directory} $out
            chmod +w -R $out

            # Create a proper lock file for the test flake
            export HOME=$(mktemp -d)
            nix flake lock $out \
              --extra-experimental-features 'nix-command flakes' \
              --override-input nixpkgs ${clan-core.inputs.nixpkgs} \
              --override-input clan-core ${clan-core-flake} \
              --override-input clan-core/flake-parts ${clan-core.inputs.flake-parts} \
              --override-input clan-core/treefmt-nix ${clan-core.inputs.treefmt-nix} \
              --override-input clan-core/nix-select ${clan-core.inputs.nix-select} \
              --override-input clan-core/data-mesher ${clan-core.inputs.data-mesher} \
              --override-input clan-core/sops-nix ${clan-core.inputs.sops-nix} \
              --override-input clan-core/disko ${clan-core.inputs.disko} \
              --override-input clan-core/systems ${clan-core.inputs.systems} \
              --override-input systems 'path://${config.clan.test.systemsFile}'

            nix flake info $out --extra-experimental-features 'nix-command flakes'
          '';
    in
    {
      options = {
        clanSettings = mkOption {
          default = { };
          type = types.submodule {
            options = {
              clan-core = mkOption { default = self; };
              nixpkgs = mkOption { default = self.inputs.nixpkgs; };
              nix-darwin = mkOption { default = self.inputs.nix-darwin; };
            };
          };
        };

        clan = mkOption {
          default = { };
          type = types.submoduleWith {
            specialArgs = {
              self = throw ''
                'self' is banned in the use of clan.services
                Use 'exports' instead: https://clan.lol/docs/unstable/reference/options/clan_service#exports
                ---
                If you really need to used 'self' here, that makes the module less portable
              '';
              inherit (config.clanSettings)
                clan-core
                nixpkgs
                nix-darwin
                ;
            };
            modules = [
              clan-core.modules.clan.default
              {
                self = {
                  inputs = {
                    # Simulate flake: 'self.inputs.self'
                    # Needed because local modules are imported from inputs.self
                    self = config;
                    set_inputs_in_tests_fixture_warning = throw "'self.inputs' within test needs to be set manually. Set 'clan.self.inputs' to mock inputs=`{}`";
                  };
                };
                _prefix = [
                  "checks"
                  "<system>"
                  config.name
                  "config"
                  "clan"
                ];
              }
              {
                options = {
                  test.useContainers = mkOption {
                    default = true;
                    type = types.bool;
                    description = "Whether to use containers for the test.";
                  };
                  test.fromFlake = mkOption {
                    default = null;
                    type = types.nullOr types.path;
                    description = ''
                      path to a directory containing a `flake.nix` defining the clan

                      Only use this if the clan CLI needs to be used inside the test.
                      Otherwise, use the other clan.XXX options instead to specify the clan.

                      Loads the clan from a flake instead of using clan.XXX options.
                      This has the benefit that a real flake.nix will be available in the test.
                      This is useful to test CLI interactions which require a flake.nix.

                      Using this introduces dependencies that should otherwise be avoided.
                    '';
                  };
                  test.flakeForSandbox = mkOption {
                    default = flakeForSandbox;
                    type = types.path;
                    description = "The flake.nix to use for the test.";
                    readOnly = true;
                  };
                  test.flake = mkOption {
                    default = clanFlakeResult;
                    type = types.raw;
                    description = "The clan flake evaluated to access attributes at test eval time";
                    readOnly = true;
                  };
                  test.machinesCross = mkOption {
                    default = machinesCross;
                    type = types.raw;
                    description = "The machines built for all supported platforms";
                    readOnly = true;
                  };
                  test.systemsFile = mkOption {
                    default = builtins.toFile "flake.systems.nix" ''
                      [ "${hostPkgs.stdenv.hostPlatform.system}" ]
                    '';
                    type = types.path;
                    description = "The systems.nix file for the test flake.";
                    readOnly = true;
                  };
                };
              }
            ];
          };
        };
      };
      config = {
        clan.directory = mkIf (config.clan.test.fromFlake != null) (mkForce config.clan.test.fromFlake);

        # Point getPublicValue at the merged dir with generated vars.
        # Service modules pass this to getPublicValue which checks it before `directory`.
        clan.varsDirectory = mergedTestDir;

        # Hard-fail if a test mixes `useContainers = true` (default) with user
        # `nodes.<name> = {...}` definitions. Those user defs would land on a
        # bare (non-clan) QEMU node submodule; the `defaults` block below would
        # then fault trying to evaluate `config.clan.core.vars.generators` on
        # a node that never imported the clan module -- surfacing as
        # `attribute 'generators' missing` from lib/test/age.nix.
        # Inspect each definition's raw attrNames; lazyAttrsOf means we get
        # names without forcing submodule evaluation, so the diagnostic fires
        # before the confusing downstream error.
        _module.check =
          let
            # Collect all attribute names contributed across all definitions of
            # `options.nodes`. Each definition.value is an attrset of
            # node-name -> submodule; `attrNames` on it doesn't force the
            # submodule bodies.
            allNodeNames = lib.concatMap builtins.attrNames options.nodes.definitions;
          in
          lib.throwIf (config.clan.test.useContainers && allNodeNames != [ ]) ''
            clan.test.useContainers = true: clan machines live on `containers.<name>`,
            not `nodes.<name>`.

            Rename every `nodes.<name> = {...}` to `containers.<name> = {...}` in this
            test, and update any `config.nodes.*` references in testScript to
            `config.containers.*`.

            Offending node name(s): ${lib.concatStringsSep ", " allNodeNames}
          '' true;

        # Inherit all nodes from the clan
        # i.e. nodes.jon <- clan.machines.jon
        # clanInternals.nixosModules contains nixosModules per node
        nodes = lib.mkIf (!config.clan.test.useContainers) machineModules;
        containers = lib.mkIf config.clan.test.useContainers machineModules;

        # When using containers, upstream nodesCompat is empty because
        # config.nodes is empty. testScript.nix uses nodesCompat to build
        # the { nodes, ... } arg passed to testScript functions and checks
        # v.virtualisation.useNixStoreImage (QEMU-only). Wrap container
        # configs with the missing attr so test scripts that reference
        # nodes.X.config.path still work.
        nodesCompat = lib.mkIf config.clan.test.useContainers (
          lib.mapAttrs (
            _: v:
            v
            // {
              virtualisation = v.virtualisation // {
                useNixStoreImage = false;
              };
            }
          ) config.containers
        );

        # Upstream requires the `devnet` system feature (`/dev/net` in the build
        # sandbox) when a test has both VMs and containers, to let them talk over
        # the network. clan tests are homogeneous -- every machine is a container
        # (useContainers = true) or every machine is a VM -- so that VM<->container
        # path never exists. But nodesCompat above intentionally mirrors the
        # containers into `nodes` so testScript `nodes.<name>` references resolve,
        # which trips the heuristic into demanding devnet. Force it off; container
        # <->container traffic uses the veth bridge, not /dev/net.
        requiredFeatures.devnet = lib.mkForce false;

        # !WARNING: Write a detailed comment if adding new options here
        # We should be very careful about adding new options here because it affects all tests
        # Keep in mind:
        # - tests should be close to the real world as possible
        # - ensure stability: in clan-core and downstream
        # - ensure that the tests are fast and reliable
        defaults = (
          { config, ... }:
          {
            imports = [
              # Speed up evaluation
              clanLib.test.minifyModule

              # Setup for age secret backend during tests
              # Provisions a static age machine key and sets secretStore = "age"
              clanLib.test.ageModule
            ];

            # Point settings.directory at the merged dir with generated vars/secrets.
            # This is an IFD: the generatedVarsDir derivation is built during eval
            # so that age.nix and in_repo.nix can find .age and value files.
            # Priority 75 overrides forName.nix (100) but yields to mkForce (50)
            # so tests with their own fixtures can override with mkForce.
            clan.core.settings.directory = lib.mkOverride 75 mergedTestDir;

            # Disable garbage collection during the test
            # https://nix.dev/manual/nix/2.28/command-ref/conf-file.html?highlight=min-free#available-settings
            nix.settings.min-free = 0;

            # This is typically set once via vars generate for a machine
            # Since we have ephemeral machines, we set it here for the test
            system.stateVersion = config.system.nixos.release;

            # Make the test depend on its vars-check derivation to reduce CI jobs
            environment.etc."clan-vars-check".source = vars-check;
          }
        );

        # Sandbox workarounds for nspawn containers not covered by upstream.
        # Upstream baseNspawnOS handles UsePAM, useDHCP, info docs, and PAM login,
        # but these settings are needed because clan tests run inside the nix build
        # sandbox where additional operations are restricted.
        containerDefaults = {
          # SCHED_BATCH requires CAP_SYS_NICE, unavailable in the sandbox
          systemd.services.nix-daemon.serviceConfig.CPUSchedulingPolicy = lib.mkForce "";
          # ioprio_set() calls require CAP_SYS_ADMIN which isn't necessarily
          # granted inside nspawn+sandbox. Clear both class and priority so
          # systemd doesn't attempt the call and fail the unit at fork time.
          systemd.services.nix-daemon.serviceConfig.IOSchedulingClass = lib.mkForce "";
          systemd.services.nix-daemon.serviceConfig.IOSchedulingPriority = lib.mkForce "";
          # Surface daemon stderr into the test log so nix-daemon failures on
          # first connect are visible.
          systemd.services.nix-daemon.serviceConfig.StandardError = lib.mkForce "journal+console";
          # Sandboxed builds need unshare()/mount() inside the nspawn
          # container; nspawn's capability set + seccomp interact badly with
          # nix's sandbox setup. Disable nix's sandbox for nested builds.
          nix.settings.sandbox = lib.mkForce false;
          # SUID wrappers need filesystem setuid bits, impossible in the sandbox
          systemd.services.suid-sgid-wrappers.enable = false;
          # resolvconf sets POSIX ACLs unsupported in the sandbox
          systemd.services.resolvconf.enable = false;
          # systemd-ssh-proxy Include directives point at store paths owned by
          # nobody:nogroup in the sandbox; OpenSSH refuses wrong-ownership configs
          programs.ssh.systemd-ssh-proxy.enable = false;
          # upstream container-config.nix defaults useHostResolvConf to true,
          # which conflicts with systemd-resolved (used by useNetworkd)
          networking.useHostResolvConf = lib.mkForce false;
        };

        extraPythonPackages = _p: [
          clan-core.legacyPackages.${hostPkgs.stdenv.hostPlatform.system}.nixosTestLib
        ];

        result = {
          inherit machinesCross;
        };
      };
    };
}
