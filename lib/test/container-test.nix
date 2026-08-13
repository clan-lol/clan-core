test:
{ pkgs, self, ... }:
let
  inherit (pkgs) lib;
  nixos-lib = import (pkgs.path + "/nixos/lib") { };
in
(nixos-lib.runTest {
  hostPkgs = pkgs;
  # speed-up evaluation
  defaults = (
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
          nix.settings.min-free = 0;
          system.stateVersion = config.system.nixos.release;
        }
      ];
    }
  );

  # Sandbox workarounds not covered by upstream baseNspawnOS.
  containerDefaults = {
    systemd.services.nix-daemon.serviceConfig.CPUSchedulingPolicy = lib.mkForce "";
    systemd.services.suid-sgid-wrappers.enable = false;
    systemd.services.resolvconf.enable = false;
    programs.ssh.systemd-ssh-proxy.enable = false;
    # upstream container-config.nix defaults useHostResolvConf to true,
    # which conflicts with systemd-resolved (used by useNetworkd)
    networking.useHostResolvConf = lib.mkForce false;
  };

  # TODO: Remove this. We should not pass special args in the test framework
  # Instead each test can forward the special args it needs
  # to accept external dependencies such as disko
  node.specialArgs.self = self;
  _module.args = { inherit self; };

  imports = [
    test
  ];
}).config.result
