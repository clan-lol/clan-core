{
  module,
  clanLib,
  ...
}:
let
  testFlake = (clanLib.clan {
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
in
{
  test_peers = {
    expr = {
      hasNetworkIds = testFlake.nixosConfigurations.jon.config.services.zerotierone.joinNetworks;
      isController =
        testFlake.nixosConfigurations.jon.config.clan.core.networking.zerotier.controller.enable;
      networkName = testFlake.nixosConfigurations.jon.config.clan.core.networking.zerotier.name;
    };
    expected = {
      hasNetworkIds = [ "0e28cb903344475e" ];
      isController = false;
      networkName = "zerotier";
    };
  };
  test_moon = {
    expr = {
      hasNetworkIds = testFlake.nixosConfigurations.sara.config.services.zerotierone.joinNetworks;
      isController =
        testFlake.nixosConfigurations.sara.config.clan.core.networking.zerotier.controller.enable;
      networkName = testFlake.nixosConfigurations.sara.config.clan.core.networking.zerotier.name;
    };
    expected = {
      hasNetworkIds = [ "0e28cb903344475e" ];
      isController = false;
      networkName = "zerotier";
    };
  };
  test_controller = {
    expr = {
      hasNetworkIds = testFlake.nixosConfigurations.bam.config.services.zerotierone.joinNetworks;
      isController =
        testFlake.nixosConfigurations.bam.config.clan.core.networking.zerotier.controller.enable;
      networkName = testFlake.nixosConfigurations.bam.config.clan.core.networking.zerotier.name;
    };
    expected = {
      hasNetworkIds = [ "0e28cb903344475e" ];
      isController = true;
      networkName = "zerotier";
    };
  };
}
