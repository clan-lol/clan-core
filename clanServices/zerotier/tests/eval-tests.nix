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
  test_peer_roles = {
    expr = {
      roles = testFlake.nixosConfigurations.jon.config.clan.core.networking.zerotier._roles;
      networkName = testFlake.nixosConfigurations.jon.config.clan.core.networking.zerotier.name;
      enabled = testFlake.nixosConfigurations.jon.config.services.zerotierone.enable;
    };
    expected = {
      roles = [ "peer" ];
      networkName = "zerotier";
      enabled = true;
    };
  };
  test_moon_roles = {
    expr = {
      roles = testFlake.nixosConfigurations.sara.config.clan.core.networking.zerotier._roles;
      networkName = testFlake.nixosConfigurations.sara.config.clan.core.networking.zerotier.name;
      enabled = testFlake.nixosConfigurations.sara.config.services.zerotierone.enable;
    };
    expected = {
      roles = [
        "moon"
        "peer"
      ];
      networkName = "zerotier";
      enabled = true;
    };
  };
  test_controller_roles = {
    expr = {
      roles = testFlake.nixosConfigurations.bam.config.clan.core.networking.zerotier._roles;
      networkName = testFlake.nixosConfigurations.bam.config.clan.core.networking.zerotier.name;
      enabled = testFlake.nixosConfigurations.bam.config.services.zerotierone.enable;
    };
    expected = {
      roles = [
        "controller"
        "peer"
      ];
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
  test_no_moon_roles = {
    expr = {
      peerRoles = testFlakeNoMoon.nixosConfigurations.jon.config.clan.core.networking.zerotier._roles;
      controllerRoles =
        testFlakeNoMoon.nixosConfigurations.bam.config.clan.core.networking.zerotier._roles;
      saraRoles = testFlakeNoMoon.nixosConfigurations.sara.config.clan.core.networking.zerotier._roles;
    };
    expected = {
      peerRoles = [ "peer" ];
      controllerRoles = [
        "controller"
        "peer"
      ];
      saraRoles = [ "peer" ];
    };
  };
}
