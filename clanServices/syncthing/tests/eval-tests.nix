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

      machines.machine1 = {
        nixpkgs.hostPlatform = "x86_64-linux";
      };
      machines.machine2 = {
        nixpkgs.hostPlatform = "x86_64-linux";
      };
      machines.machine3 = {
        nixpkgs.hostPlatform = "x86_64-linux";
      };
      machines.machine4 = {
        nixpkgs.hostPlatform = "x86_64-linux";
      };

      modules.syncthing = module;

      inventory.instances = {
        default = {
          module.name = "syncthing";
          module.input = "self";

          roles.peer.tags.all = { };
          roles.peer.settings.extraDevices.phone = {
            id = "P56IOI7-MZJNU2Y-IQGDREY-DM2MGTI-MGL3BXN-PQ6W5BM-TBBZ4TJ-XZWICQ2";
          };
        };
      };
    }).config;
in
{
  # Test structural configuration without requiring generated vars.
  # Device IDs require pre-generated vars (getPublicValue reads from disk),
  # so we only test properties that don't depend on generated values.
  test_syncthing_enabled = {
    expr = {
      enabled = testFlake.nixosConfigurations.machine1.config.services.syncthing.enable;
      configDir = testFlake.nixosConfigurations.machine1.config.services.syncthing.configDir;
      group = testFlake.nixosConfigurations.machine1.config.services.syncthing.group;
    };
    expected = {
      enabled = true;
      configDir = "/var/lib/syncthing";
      group = "syncthing";
    };
  };

  test_generator_defined = {
    expr = {
      hasGenerator = testFlake.nixosConfigurations.machine1.config.clan.core.vars.generators ? syncthing;
      files = lib.attrNames testFlake.nixosConfigurations.machine1.config.clan.core.vars.generators.syncthing.files;
    };
    expected = {
      hasGenerator = true;
      files = [
        "api"
        "cert"
        "id"
        "key"
      ];
    };
  };
}
