test:
{ pkgs, self, ... }:
let
  inherit (pkgs) lib;
  nixos-lib = import (pkgs.path + "/nixos/lib") { };
in
(nixos-lib.runTest {
  hostPkgs = pkgs;
  # speed-up evaluation
  defaults =
    { config, options, ... }:
    {
      imports = [
        self.clanLib.test.minifyModule
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

          # We use networkd to assign static ip addresses
          networking.useNetworkd = true;
          services.resolved.enable = false;

          # Rename the host0 interface to eth0 to match what we expect in VM tests.
          system.activationScripts.renameInterface = ''
            ${pkgs.iproute2}/bin/ip link set dev host0 name eth1
          '';

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
}).config.result
