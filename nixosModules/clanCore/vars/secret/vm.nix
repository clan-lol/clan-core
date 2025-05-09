{
  config,
  lib,
  ...
}:
{
  config.clan.core.vars.settings = lib.mkIf (config.clan.core.vars.settings.secretStore == "vm") {
    fileModule = file: {
      path = lib.mkIf (file.config.secret == true) (
        if file.config.neededFor == "partitioning" then
          "/run/partitioning-secrets/${file.config.generatorName}/${file.config.name}"
        else
          "/etc/secrets/${file.config.generatorName}/${file.config.name}"
      );
    };
    secretModule = "clan_cli.vars.secret_modules.vm";
  };
}
