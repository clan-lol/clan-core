{
  lib,
  self,
  config,
  ...
}:
let
  inherit (lib)
    flatten
    mapAttrsToList
    mkForce
    mkIf
    mkOption
    types
    unique
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
        flip
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

      machineModules' = flip filterAttrs clanFlakeResult.nixosModules (
        name: _module: hasPrefix "clan-machine-" name
      );

      machineModules = flip mapAttrs' machineModules' (
        name: machineModule: {
          name = removePrefix "clan-machine-" name;
          value = machineModule;
        }
      );

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

      update-vars-script = "${
        self.packages.${hostPkgs.system}.generate-test-vars
      }/bin/generate-test-vars";

      relativeDir = removePrefix "${self}/" (toString config.clan.directory);

      update-vars = hostPkgs.writeShellScriptBin "update-vars" ''
        ${update-vars-script} $PRJ_ROOT/${relativeDir} ${testName}
      '';

      testSrc = lib.cleanSource config.clan.directory;

      inputsForMachine =
        machine:
        flip mapAttrsToList machine.clan.core.vars.generators (_name: generator: generator.runtimeInputs);

      generatorScripts =
        machine:
        flip mapAttrsToList machine.clan.core.vars.generators (_name: generator: generator.finalScript);

      generatorRuntimeInputs = unique (
        flatten (flip mapAttrsToList config.nodes (_machineName: machine: inputsForMachine machine))
      );

      allGeneratorScripts = unique (
        flatten (flip mapAttrsToList config.nodes (_machineName: machine: generatorScripts machine))
      );

      vars-check =
        hostPkgs.runCommand "update-vars-check-${testName}"
          {
            nativeBuildInputs = generatorRuntimeInputs ++ [
              hostPkgs.nix
              hostPkgs.git
              hostPkgs.age
              hostPkgs.sops
              hostPkgs.bubblewrap
            ];
            closureInfo = hostPkgs.closureInfo {
              rootPaths =
                generatorRuntimeInputs
                ++ allGeneratorScripts
                ++ [
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
              inherit (config.clanSettings)
                clan-core
                nixpkgs
                nix-darwin
                ;
              # By default clan.directory defaults to self, but we don't
              # have a sensible default for self here
              self = throw "set clan.directory in the test";
            };
            modules = [
              clan-core.modules.clan.default
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
          }
        );

        result = {
          inherit update-vars vars-check machinesCross;
        };
      };
    };
}
