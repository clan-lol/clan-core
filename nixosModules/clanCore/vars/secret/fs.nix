{
  config,
  lib,
  ...
}:
{
  # TODO: move into a single structure
  config.clan.core.vars.settings.fileModule =
    lib.mkIf (config.clan.core.vars.settings.secretStore == "fs")
      (file: {
        path =
          if file.config.neededFor == "partitioning" then
            throw "${file.config.generatorName}/${file.config.name}: FS backend does not support partitioning."
          else
            "/run/secrets/${file.config.generatorName}/${file.config.name}";
      });

}
