{ config, lib, ... }:
{
  config.clan.core.vars.settings =
    lib.mkIf (config.clan.core.vars.settings.publicStore == "in_repo")
      {
        publicModule = "clan_cli.vars.public_modules.in_repo";
        fileModule = file: {
          path =
            config.clan.core.clanDir + "/machines/${config.clan.core.machineName}/vars/${file.config.name}";
        };
      };
}
