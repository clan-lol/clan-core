{
  inputs.clan-core.url = "https://__replace__";
  inputs.nixpkgs.url = "https://__replace__";
  inputs.clan-core.inputs.nixpkgs.follows = "nixpkgs";
  inputs.systems.url = "https://__systems__";
  inputs.systems.flake = false;

  outputs =
    {
      self,
      clan-core,
      systems,
      ...
    }:
    let
      inherit (clan-core.inputs.nixpkgs) lib;

      # Usage see: https://docs.clan.lol
      clan = clan-core.lib.clan {
        inherit self;

        machines.peer1.nixpkgs.hostPlatform = lib.head (import systems);

        inventory =
          { ... }:
          {
            meta.name = "foo";
            meta.domain = "foo";
            machines.peer1 = { };
          };
      };
    in
    {
      # all machines managed by Clan
      inherit (clan.config) nixosConfigurations nixosModules clanInternals;
    };
}
