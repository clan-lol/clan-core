# Clan configuration file
# TODO: This file is used as a template for the simple GUI workflow
{
  inputs.clan-core.url = "git+file:///home/johannes/git/clan-core";
  outputs =
    { self, clan-core, ... }:
    let
      clan = clan-core.lib.buildClan {
        # This clan builds all its configuration out of the current directory
        directory = self;
      };
    in
    {
      inherit (clan) nixosConfigurations clanInternals;
    };
}
