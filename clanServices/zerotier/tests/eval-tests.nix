{
  module,
  clanLib,
  lib,
  ...
}:
let
  testFlake =
    (clanLib.clan {
      self = { };
      directory = ./vm;

      machines.jon = {
        nixpkgs.hostPlatform = "x86_64-linux";
      };
      machines.sara = {
        nixpkgs.hostPlatform = "x86_64-linux";
      };
      machines.bam = {
        nixpkgs.hostPlatform = "x86_64-linux";
      };

      modules.zerotier = module;

      inventory.instances = {
        zerotier = {
          module.name = "zerotier";
          module.input = "self";

          roles.peer.tags.all = { };
          roles.moon.machines.sara.settings.stableEndpoints = [ "10.0.0.3/9993" ];
          roles.controller.machines.bam = { };
        };
      };
    }).config;

  testFlakeNoMoon =
    (clanLib.clan {
      self = { };
      directory = ./vm;

      machines.jon = {
        nixpkgs.hostPlatform = "x86_64-linux";
      };
      machines.sara = {
        nixpkgs.hostPlatform = "x86_64-linux";
      };
      machines.bam = {
        nixpkgs.hostPlatform = "x86_64-linux";
      };

      modules.zerotier = module;

      inventory.instances = {
        zerotier = {
          module.name = "zerotier";
          module.input = "self";

          roles.peer.tags.all = { };
          roles.controller.machines.bam = { };
        };
      };
    }).config;

  cfg = machine: testFlake.nixosConfigurations.${machine}.config;
  cfgNoMoon = machine: testFlakeNoMoon.nixosConfigurations.${machine}.config;
in
# Assert the service sets some critical downstream NixOS options
{
  test_peer_nixos_config = {
    expr = {
      enabled = (cfg "jon").services.zerotierone.enable;
      firewallTcp = builtins.elem 9993 (cfg "jon").networking.firewall.allowedTCPPorts;
      firewallUdp = builtins.elem 9993 (cfg "jon").networking.firewall.allowedUDPPorts;
      nmUnmanaged = builtins.elem "interface-name:zt*" (cfg "jon").networking.networkmanager.unmanaged;
      tcpFallback = (cfg "jon").services.zerotierone.localConf.settings.tcpFallbackRelay;
    };
    expected = {
      enabled = true;
      firewallTcp = true;
      firewallUdp = true;
      nmUnmanaged = true;
      tcpFallback = "65.21.12.51/4443";
    };
  };

  test_controller_nixos_config = {
    expr = {
      enabled = (cfg "bam").services.zerotierone.enable;
      stateFolders = (cfg "bam").clan.core.state.zerotier.folders;
      autoAcceptWantedBy = (cfg "bam").systemd.services.zerotier-inventory-autoaccept.wantedBy;
      autoAcceptAfterZt = builtins.elem "zerotierone.service" (cfg "bam")
      .systemd.services.zerotier-inventory-autoaccept.after;
      hasEtcNetworkId = (cfg "bam").environment.etc ? "zerotier/network-id";
    };
    expected = {
      enabled = true;
      stateFolders = [ "/var/lib/zerotier-one" ];
      autoAcceptWantedBy = [ "multi-user.target" ];
      autoAcceptAfterZt = true;
      hasEtcNetworkId = true;
    };
  };

  test_moon_nixos_config = {
    expr = {
      enabled = (cfg "sara").services.zerotierone.enable;
    };
    expected = {
      enabled = true;
    };
  };

  test_controller_generator_structure = {
    expr = {
      sharedShare = (cfg "bam").clan.core.vars.generators.zerotier-controller.share;
      sharedFiles = lib.attrNames (cfg "bam").clan.core.vars.generators.zerotier-controller.files;
      perMachineDeps = (cfg "bam").clan.core.vars.generators.zerotier.dependencies;
      perMachineFiles = lib.attrNames (cfg "bam").clan.core.vars.generators.zerotier.files;
    };
    expected = {
      sharedShare = true;
      sharedFiles = [
        "zerotier-identity-secret"
        "zerotier-ip"
        "zerotier-network-id"
      ];
      perMachineDeps = [ "zerotier-controller" ];
      perMachineFiles = [
        "zerotier-identity-secret"
        "zerotier-ip"
        "zerotier-network-id"
      ];
    };
  };

  test_peer_generator_structure = {
    expr = {
      dependencies = (cfg "jon").clan.core.vars.generators.zerotier.dependencies;
      files = lib.attrNames (cfg "jon").clan.core.vars.generators.zerotier.files;
    };
    expected = {
      dependencies = [ "zerotier-controller" ];
      files = [
        "zerotier-identity-secret"
        "zerotier-ip"
      ];
    };
  };

  test_networkd_config = {
    expr = (cfg "jon").systemd.network.networks."09-zerotier".matchConfig.Name;
    expected = "zt*";
  };

  test_no_moon_config = {
    expr = {
      enabled = (cfgNoMoon "sara").services.zerotierone.enable;
    };
    expected = {
      enabled = true;
    };
  };

  # Without this, ZT can route through overlay networks (e.g. Yggdrasil) that
  # themselves peer over ZT, causing recursive encapsulation.
  test_interface_prefix_blacklist = {
    expr = (cfg "bam").services.zerotierone.localConf.settings.interfacePrefixBlacklist;
    expected = [
      "ygg"
      "hyprspace"
      "tinc"
      "tailscale"
      "mycelium"
      "wg"
      "zt"
    ];
  };
}
