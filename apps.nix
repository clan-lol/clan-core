{ lib, ... }:

{
  perSystem =
    { config, ... }:
    {
      apps = {
        clan-cli = {
          type = "app";
          program = lib.getExe config.packages.clan-cli;
        };
        default = config.apps.clan-cli;
      };
    };
}
