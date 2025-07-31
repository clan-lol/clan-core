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
  test_machine1_peers = {
    expr = {
      devices = lib.attrNames testFlake.nixosConfigurations.machine1.config.services.syncthing.settings.devices;
      machine4_ID =
        testFlake.nixosConfigurations.machine1.config.services.syncthing.settings.devices.machine1.id;
      externalPhoneId =
        testFlake.nixosConfigurations.machine1.config.services.syncthing.settings.devices.phone.id;
    };
    expected = {
      devices = [
        "machine1"
        "machine2"
        "machine3"
        "machine4"
        "phone"
      ];
      machine4_ID = "LJOGYGS-RQPWIHV-HD4B3GK-JZPVPK6-VI3IAY5-CWQWIXK-NJSQMFH-KXHOHA4";
      externalPhoneId = "P56IOI7-MZJNU2Y-IQGDREY-DM2MGTI-MGL3BXN-PQ6W5BM-TBBZ4TJ-XZWICQ2";
    };
  };
}
