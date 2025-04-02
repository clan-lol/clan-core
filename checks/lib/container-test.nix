test:
{ pkgs, self, ... }:
let
  inherit (pkgs) lib;
  nixos-lib = import (pkgs.path + "/nixos/lib") { };
in
(nixos-lib.runTest (
  { hostPkgs, ... }:
  {
    hostPkgs = pkgs;
    # speed-up evaluation
    defaults =
      { config, options, ... }:
      {
        imports = [
          ./minify.nix
        ];
        config = lib.mkMerge [
          (lib.optionalAttrs (options ? clan) {
            clan.core.settings.machine.name = config.networking.hostName;
          })
          {
            documentation.enable = lib.mkDefault false;
            boot.isContainer = true;

            # needed since nixpkgs 7fb2f407c01b017737eafc26b065d7f56434a992 removed the getty unit by default
            console.enable = true;

            # undo qemu stuff
            system.build.initialRamdisk = "";
            virtualisation.sharedDirectories = lib.mkForce { };
            networking.useDHCP = false;

            # we have not private networking so far
            networking.interfaces = lib.mkForce { };
            #networking.primaryIPAddress = lib.mkForce null;
            systemd.services.backdoor.enable = false;

            # we don't have permission to set cpu scheduler in our container
            systemd.services.nix-daemon.serviceConfig.CPUSchedulingPolicy = lib.mkForce "";
          }
        ];
      };
    # to accept external dependencies such as disko
    node.specialArgs.self = self;
    _module.args = { inherit self; };
    imports = [
      test
      ./container-driver/module.nix
    ];
  }
)).config.result
