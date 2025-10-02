{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/monitoring";
  manifest.description = "Monitoring service for the nodes in your clan";
  manifest.readme = builtins.readFile ./README.md;

  roles.telegraf = {
    description = "Placeholder role to apply the telegraf monitoring agent";
    interface =
      { lib, ... }:
      {
        options.allowAllInterfaces = lib.mkOption {
          type = lib.types.nullOr lib.types.bool;
          default = null;
          description = "Deprecated. Has no effect.";
        };

        options.interfaces = lib.mkOption {
          type = lib.types.nullOr (lib.types.listOf lib.types.str);
          default = null;
          description = "Deprecated. Has no effect.";
        };
      };
  };

  imports = [ ./telegraf.nix ];
}
