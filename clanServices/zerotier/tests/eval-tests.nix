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
      autoAcceptWantedBy = (cfg "bam").systemd.services.zerotier-autoaccept-zerotier.wantedBy;
      autoAcceptAfterZt = builtins.elem "zerotierone.service" (cfg "bam")
      .systemd.services.zerotier-autoaccept-zerotier.after;
    };
    expected = {
      enabled = true;
      stateFolders = [ "/var/lib/zerotier-one" ];
      autoAcceptWantedBy = [ "multi-user.target" ];
      autoAcceptAfterZt = true;
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

  # Shared generators: controller identity + network-id
  test_controller_shared_generators = {
    expr = {
      identityShare = (cfg "bam").clan.core.vars.generators.zerotier-identity-bam.share;
      identityFiles = lib.attrNames (cfg "bam").clan.core.vars.generators.zerotier-identity-bam.files;
      identityDeploy =
        (cfg "bam").clan.core.vars.generators.zerotier-identity-bam.files.identity-secret.deploy;
      networkShare = (cfg "bam").clan.core.vars.generators.zerotier-network-zerotier.share;
      networkFiles = lib.attrNames (cfg "bam").clan.core.vars.generators.zerotier-network-zerotier.files;
      networkDeps = (cfg "bam").clan.core.vars.generators.zerotier-network-zerotier.dependencies;
    };
    expected = {
      identityShare = true;
      identityFiles = [ "identity-secret" ];
      identityDeploy = false;
      networkShare = true;
      networkFiles = [ "network-id" ];
      networkDeps = [ "zerotier-identity-bam" ];
    };
  };

  # Per-machine identity generator
  test_identity_generator = {
    expr = {
      # Controller copies from shared
      controllerDeps = (cfg "bam").clan.core.vars.generators.zerotier-identity.dependencies;
      controllerFiles = lib.attrNames (cfg "bam").clan.core.vars.generators.zerotier-identity.files;
      # Peer generates fresh (no deps on shared identity)
      peerDeps = (cfg "jon").clan.core.vars.generators.zerotier-identity.dependencies;
      peerFiles = lib.attrNames (cfg "jon").clan.core.vars.generators.zerotier-identity.files;
    };
    expected = {
      controllerDeps = [ "zerotier-identity-bam" ];
      controllerFiles = [ "identity-secret" ];
      peerDeps = [ ];
      peerFiles = [ "identity-secret" ];
    };
  };

  # Per-instance IP generator
  test_instance_ip_generator = {
    expr = {
      peerDeps = (cfg "jon").clan.core.vars.generators.zerotier-ip-zerotier.dependencies;
      peerFiles = lib.attrNames (cfg "jon").clan.core.vars.generators.zerotier-ip-zerotier.files;
      controllerDeps = (cfg "bam").clan.core.vars.generators.zerotier-ip-zerotier.dependencies;
    };
    expected = {
      peerDeps = [
        "zerotier-identity"
        "zerotier-network-zerotier"
      ];
      peerFiles = [ "ip" ];
      controllerDeps = [
        "zerotier-identity"
        "zerotier-network-zerotier"
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
