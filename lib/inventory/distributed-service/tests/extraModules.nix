{ clanLib }:
let
  clan = clanLib.clan {
    self = { };
    directory = ./.;

    machines.jon = {
      nixpkgs.hostPlatform = "x86_64-linux";

    };
    # A module that adds exports perMachine
    modules.A = {
      manifest.name = "A";
      roles.peer = { };
    };

    inventory = {
      instances.A = {
        module.input = "self";
        roles.peer.tags.all = { };

        roles.peer.extraModules = [ ./oneOption.nix ];
      };
    };
  };
in
{
  test_1 = {
    inherit clan;
    expr = clan.config.nixosConfigurations.jon.config.testDebug;
    expected = 42;
  };
}
