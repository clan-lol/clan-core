{
  lib,
  clanLib,
}:
let
  inherit (lib)
    mkOption
    removePrefix
    types
    mapAttrsToList
    flip
    unique
    flatten
    ;

in
{
  #
  containerTest = import ./container-test.nix;
  baseTest = import ./test-base.nix;
  #
  flakeModules = clanLib.callLib ./flakeModules.nix { };

  minifyModule = ./minify.nix;
  sopsModule = ./sops.nix;
  # A function that returns an extension to runTest
  # TODO: remove this from clanLib, add to legacyPackages, simplify signature
  makeTestClan =
    {
      nixosTest,
      pkgs,
      self,
      useContainers ? true,
      # Displayed for better error messages, otherwise the placeholder
      attrName ? "<check_name>",
      ...
    }:
    let
      nixos-lib = import (pkgs.path + "/nixos/lib") { };

      testName = test.config.name;

      update-vars-script = "${self.packages.${pkgs.system}.generate-test-vars}/bin/generate-test-vars";

      relativeDir = removePrefix ("${self}/") (toString test.config.clan.directory);

      update-vars = pkgs.writeShellScriptBin "update-vars" ''
        ${update-vars-script} $PRJ_ROOT/${relativeDir} ${testName}
      '';

      testSrc = lib.cleanSource test.config.clan.directory;

      inputsForMachine =
        machine:
        flip mapAttrsToList machine.clan.core.vars.generators (_name: generator: generator.runtimeInputs);

      generatorRuntimeInputs = unique (
        flatten (flip mapAttrsToList test.config.nodes (_machineName: machine: inputsForMachine machine))
      );

      vars-check =
        pkgs.runCommand "update-vars-check"
          {
            nativeBuildInputs = generatorRuntimeInputs ++ [
              pkgs.nix
              pkgs.git
              pkgs.age
              pkgs.sops
              pkgs.bubblewrap
            ];
            closureInfo = pkgs.closureInfo {
              rootPaths = generatorRuntimeInputs ++ [
                pkgs.bash
                pkgs.coreutils
                pkgs.jq.dev
                pkgs.stdenv
                pkgs.stdenvNoCC
                pkgs.shellcheck-minimal
                pkgs.age
                pkgs.sops
              ];
            };
          }
          ''
            ${self.legacyPackages.${pkgs.system}.setupNixInNix}
            cp -r ${testSrc} ./src
            chmod +w -R ./src
            find ./src/sops ./src/vars | sort > filesBefore
            ${update-vars-script} ./src ${testName} \
              --repo-root ${self.packages.${pkgs.system}.clan-core-flake} \
              --clean
            find ./src/sops ./src/vars | sort > filesAfter
            if ! diff -q filesBefore filesAfter; then
              echo "The update-vars script changed the files in ${testSrc}."
              echo "Diff:"
              diff filesBefore filesAfter || true
              exit 1
            fi
            touch $out
          '';
      test =
        (nixos-lib.runTest (
          { config, ... }:
          let
            clanFlakeResult = config.clan;
          in
          {
            imports = [
              nixosTest
            ] ++ lib.optionals useContainers [ ./container-test-driver/driver-module.nix ];
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
                        attrName
                        "config"
                        "clan"
                      ];
                    }
                  ];
                };
              };
            };
            config = {
              # Inherit all nodes from the clan
              # i.e. nodes.jon <- clan.machines.jon
              # clanInternals.nixosModules contains nixosModules per node
              nodes = clanFlakeResult.clanInternals.nixosModules;

              hostPkgs = pkgs;

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

              # TODO: figure out if we really need this
              # I am proposing for less magic in the test-framework
              # People may add this in their own tests
              # _module.args = { inherit self; };
              # node.specialArgs.self = self;
            };
          }
        )).config.result;
    in
    test
    // {
      inherit update-vars vars-check;
    };
}
