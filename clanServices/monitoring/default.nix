{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/monitoring";
  manifest.description = "Monitoring service for the nodes in your clan";
  manifest.readme = builtins.readFile ./README.md;

  roles.telegraf = {
    interface =
      { lib, ... }:
      {
        options.allowAllInterfaces = lib.mkOption {
          type = lib.types.bool;
          default = false;
          description = "If true, Telegraf will listen on all interfaces. Otherwise, it will only listen on the interfaces specified in `interfaces`";
        };

        options.interfaces = lib.mkOption {
          type = lib.types.listOf lib.types.str;
          default = [ "zt+" ];
          description = "List of interfaces to expose the metrics to";
        };
      };
  };

  imports = [ ./telegraf.nix ];
}
