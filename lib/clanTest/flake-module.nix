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
  # Shared nixpkgs instance for cross-platform compatibility checks.
  # Evaluated once so all clanTests can reuse it.
  flake.clanTestCrossPkgs = import self.inputs.nixpkgs {
    system = "x86_64-linux";
    crossSystem = "aarch64-linux";
  };

  # A function that returns an extension to runTest
  # TODO: remove this from clanLib, add to legacyPackages, simplify signature
  flake.modules.nixosTest.clanTest =
    { config, hostPkgs, ... }:
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

      machinesCross = lib.genAttrs [ "aarch64-darwin" "aarch64-linux" "x86_64-darwin" "x86_64-linux" ] (
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
      # Always use x86_64-linux machines: generators produce platform-independent
      # output (keys, configs) and the IFD must build on the evaluating system.
      clanNodes = lib.mapAttrs (
        _name: system: system.config
      ) clanFlakeResult.clanInternals.machines.x86_64-linux;

      # Pkgs for IFD derivations — always x86_64-linux so the derivation can
      # build on the evaluating system without requiring a remote builder.
      # Generator output is platform-independent text (keys, configs).
      ifdPkgs = clan-core.inputs.nixpkgs.legacyPackages.x86_64-linux;

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
      imports = [
        ../test/container-test-driver/driver-module.nix

      ];
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
                Use 'exports' instead: https://docs.clan.lol/reference/options/clan_service/#exports
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
                  test.skipCrossCheck = mkOption {
                    default = false;
                    type = types.bool;
                    description = "Whether to skip the cross-platform compatibility check for this test.";
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

        # Inherit all nodes from the clan
        # i.e. nodes.jon <- clan.machines.jon
        # clanInternals.nixosModules contains nixosModules per node
        nodes = machineModules;

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

        extraPythonPackages = _p: [
          clan-core.legacyPackages.${hostPkgs.stdenv.hostPlatform.system}.nixosTestLib
        ];

        result = {
          inherit machinesCross;
        };
      };
    };
}
