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

      update-vars-script = "${self.packages.${hostPkgs.system}.clan-cli}/bin/clan-generate-test-vars";

      relativeDir = removePrefix "${self}/" (toString config.clan.directory);

      update-vars = hostPkgs.writeShellScriptBin "update-vars" ''
        set -x
        export PRJ_ROOT=$(git rev-parse --show-toplevel)
        ${update-vars-script} $PRJ_ROOT/${relativeDir} ${testName}
      '';

      # Import the new Nix-based vars execution system
      varsExecutor = import ./vars-executor.nix { inherit lib; };

      vars-check = hostPkgs.runCommand "vars-check-${testName}" { } (
        varsExecutor.generateExecutionScript hostPkgs config.nodes
      );

      # the test's flake.nix with locked clan-core input
      flakeForSandbox =
        hostPkgs.runCommand "offline-flake-for-test-${config.name}"
          {
            nativeBuildInputs = [ hostPkgs.nix ];
          }
          ''
            cp -r ${config.clan.directory} $out
            chmod +w -R $out
            substituteInPlace $out/flake.nix \
              --replace-fail \
                "https://git.clan.lol/clan/clan-core/archive/main.tar.gz" \
                "${clan-core.packages.${hostPkgs.system}.clan-core-flake}"

            # Create a proper lock file for the test flake
            export HOME=$(mktemp -d)
            nix flake lock $out \
              --extra-experimental-features 'nix-command flakes' \
              --override-input clan-core ${clan-core.packages.${hostPkgs.system}.clan-core-flake} \
              --override-input nixpkgs ${clan-core.inputs.nixpkgs}
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
                };
              }
            ];
          };
        };
      };
      config = {
        clan.directory = mkIf (config.clan.test.fromFlake != null) (mkForce config.clan.test.fromFlake);

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

              # Setup for sops during tests
              # configures a static age-key to skip the age-key generation
              clanLib.test.sopsModule
            ];

            # Disable garbage collection during the test
            # https://nix.dev/manual/nix/2.28/command-ref/conf-file.html?highlight=min-free#available-settings
            nix.settings.min-free = 0;

            # This is typically set once via vars generate for a machine
            # Since we have ephemeral machines, we set it here for the test
            system.stateVersion = config.system.nixos.release;

            # Currently this is the default in NixOS, but we set it explicitly to avoid surprises
            # Disable the initrd systemd service which has the following effect
            #
            # With the below on 'false' initrd runs a 'minimal shell script', called the stage-1 init.
            # Benefits:
            #     Simple and fast.
            #     Easier to debug for very minimal or custom setups.
            # Drawbacks:
            #     Limited flexibility.
            #     Harder to handle advanced setups (like TPM, LUKS, or LVM-on-LUKS) but not needed since we are in a test
            #     No systemd journal logs from initrd.
            boot.initrd.systemd.enable = false;
            # Make the test depend on its vars-check derivation to reduce CI jobs
            environment.etc."clan-vars-check".source = vars-check;
          }
        );

        result = {
          inherit update-vars machinesCross;
        };
      };
    };
}
