{
  lib,
  self,
  config,
  ...
}:
let
  inherit (lib)
    flatten
    flip
    mapAttrs'
    mapAttrsToList
    mkOption
    removePrefix
    types
    unique
    ;

  clanLib = config.flake.clanLib;
in
{
  # A function that returns an extension to runTest
  # TODO: remove this from clanLib, add to legacyPackages, simplify signature
  flake.modules.nixosVmTest.clanTest =
    { config, hostPkgs, ... }:
    let
      clanFlakeResult = config.clan;
      testName = config.name;

      update-vars-script = "${
        self.packages.${hostPkgs.system}.generate-test-vars
      }/bin/generate-test-vars";

      relativeDir = removePrefix ("${self}/") (toString config.clan.directory);

      update-vars = hostPkgs.writeShellScriptBin "update-vars" ''
        ${update-vars-script} $PRJ_ROOT/${relativeDir} ${testName}
      '';

      testSrc = lib.cleanSource config.clan.directory;

      inputsForMachine =
        machine:
        flip mapAttrsToList machine.clan.core.vars.generators (_name: generator: generator.runtimeInputs);

      generatorRuntimeInputs = unique (
        flatten (flip mapAttrsToList config.nodes (_machineName: machine: inputsForMachine machine))
      );

      vars-check =
        hostPkgs.runCommand "update-vars-check"
          {
            nativeBuildInputs = generatorRuntimeInputs ++ [
              hostPkgs.nix
              hostPkgs.git
              hostPkgs.age
              hostPkgs.sops
              hostPkgs.bubblewrap
            ];
            closureInfo = hostPkgs.closureInfo {
              rootPaths = generatorRuntimeInputs ++ [
                hostPkgs.bash
                hostPkgs.coreutils
                hostPkgs.jq.dev
                hostPkgs.stdenv
                hostPkgs.stdenvNoCC
                hostPkgs.shellcheck-minimal
                hostPkgs.age
                hostPkgs.sops
              ];
            };
          }
          ''
            ${self.legacyPackages.${hostPkgs.system}.setupNixInNix}
            cp -r ${testSrc} ./src
            chmod +w -R ./src
            mkdir -p ./src/sops ./src/vars # create dirs case the test has no vars
            find ./src/sops ./src/vars | sort > filesBefore
            ${update-vars-script} ./src ${testName} \
              --repo-root ${self.packages.${hostPkgs.system}.clan-core-flake} \
              --clean
            mkdir -p ./src/sops ./src/vars
            find ./src/sops ./src/vars | sort > filesAfter
            if ! diff -q filesBefore filesAfter; then
              echo "The update-vars script changed the files in ${testSrc}."
              echo "Diff:"
              diff filesBefore filesAfter || true
              exit 1
            fi
            touch $out
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
              inherit (config.clanSettings)
                clan-core
                nixpkgs
                nix-darwin
                ;
            };
            modules = [
              clanLib.buildClanModule.flakePartsModule
              {
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
                };
              }
            ];
          };
        };
      };
      config = {
        # Inherit all nodes from the clan
        # i.e. nodes.jon <- clan.machines.jon
        # clanInternals.nixosModules contains nixosModules per node
        nodes = flip mapAttrs' clanFlakeResult.nixosModules (
          name: machineModule: {
            name = removePrefix "clan-machine-" name;
            value = machineModule;
          }
        );

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

            # Disable documentation
            # This is nice to speed up the evaluation
            # And also suppresses any warnings or errors about the documentation
            documentation.enable = lib.mkDefault false;

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
            # make the test depend on its vars-check derivation
            environment.variables.CLAN_VARS_CHECK = "${vars-check}";
          }
        );

        result = { inherit update-vars vars-check; };
      };
    };
}
