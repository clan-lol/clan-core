{ lib, clanLib }:
let
  inherit (lib)
    mkOption
    types
    ;

in
{
  flakeModules = clanLib.callLib ./flakeModules.nix { };

  #
  minifyModule = ./minify.nix;
  sopsModule = ./sops.nix;
  # A function that returns an extension to runTest
  makeTestClan =
    {
      nixosTest,
      pkgs,
      self,
      useContainers ? true,
      ...
    }:
    let
      nixos-lib = import (pkgs.path + "/nixos/lib") { };
    in
    (nixos-lib.runTest (
      { config, ... }:
      let
        clanFlakeResult = config.clan;
      in
      {
        imports = [
          nixosTest
        ] ++ lib.optionals (useContainers) [ ./container-test-driver/driver-module.nix ];
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
}
