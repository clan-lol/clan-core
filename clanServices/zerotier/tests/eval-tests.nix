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
in
{
  # Test structural configuration without requiring generated vars.
  # joinNetworks depends on pre-generated vars (zerotier-network-id file),
  # so we only test properties that don't depend on generated values.
  test_peer_config = {
    expr = {
      networkName = testFlake.nixosConfigurations.jon.config.clan.core.networking.zerotier.name;
      enabled = testFlake.nixosConfigurations.jon.config.services.zerotierone.enable;
    };
    expected = {
      networkName = "zerotier";
      enabled = true;
    };
  };
  test_moon_config = {
    expr = {
      networkName = testFlake.nixosConfigurations.sara.config.clan.core.networking.zerotier.name;
      enabled = testFlake.nixosConfigurations.sara.config.services.zerotierone.enable;
    };
    expected = {
      networkName = "zerotier";
      enabled = true;
    };
  };
  test_controller_config = {
    expr = {
      networkName = testFlake.nixosConfigurations.bam.config.clan.core.networking.zerotier.name;
      enabled = testFlake.nixosConfigurations.bam.config.services.zerotierone.enable;
    };
    expected = {
      networkName = "zerotier";
      enabled = true;
    };
  };
  test_generator_defined = {
    expr = {
      hasSharedGenerator =
        testFlake.nixosConfigurations.bam.config.clan.core.vars.generators ? zerotier-controller;
      sharedFiles = lib.attrNames testFlake.nixosConfigurations.bam.config.clan.core.vars.generators.zerotier-controller.files;
      hasControllerGenerator =
        testFlake.nixosConfigurations.bam.config.clan.core.vars.generators ? zerotier;
      hasPeerGenerator = testFlake.nixosConfigurations.jon.config.clan.core.vars.generators ? zerotier;
    };
    expected = {
      hasSharedGenerator = true;
      sharedFiles = [
        "zerotier-identity-secret"
        "zerotier-ip"
        "zerotier-network-id"
      ];
      hasControllerGenerator = true;
      hasPeerGenerator = true;
    };
  };
  # When no moon role is assigned, sara is a plain peer — verify she gets
  # zerotier enabled and empty stableEndpoints (the default).
  test_no_moon_config = {
    expr = {
      saraEnabled = testFlakeNoMoon.nixosConfigurations.sara.config.services.zerotierone.enable;
      saraStableEndpoints =
        testFlakeNoMoon.nixosConfigurations.sara.config.clan.core.networking.zerotier.moon.stableEndpoints;
    };
    expected = {
      saraEnabled = true;
      saraStableEndpoints = [ ];
    };
  };
  # Moon role propagates stableEndpoints from inventory settings into NixOS config.
  test_moon_stable_endpoints = {
    expr = testFlake.nixosConfigurations.sara.config.clan.core.networking.zerotier.moon.stableEndpoints;
    expected = [ "10.0.0.3/9993" ];
  };
  # ZeroTier must blacklist overlay interface prefixes to prevent recursive
  # encapsulation (e.g. ZT traffic routed through Yggdrasil which peers over ZT).
  test_interface_prefix_blacklist = {
    expr =
      testFlake.nixosConfigurations.bam.config.services.zerotierone.localConf.settings.interfacePrefixBlacklist;
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
