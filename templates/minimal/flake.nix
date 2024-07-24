{
  inputs.clan-core.url = "git+https://git.clan.lol/clan/clan-core";

  outputs =
    { self, clan-core, ... }:
    let
      # Usage see: https://docs.clan.lol
      clan = clan-core.lib.buildClan {
        meta.name = "miniclan";
        directory = self;
      };
    in
    {
      # all machines managed by Clan
      inherit (clan) nixosConfigurations clanInternals;
    };
}
