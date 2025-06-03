{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/auto-upgrade";
  manifest.description = "Automatic system upgrade for the Clan App";
  manifest.categories = [ "System" ];

  roles.default = {
    interface =
      { lib, ... }:
      {
        options.flake = lib.mkOption {
          type = lib.types.str;
          description = "Flake reference";
        };
      };

    perInstance =
      { settings, ... }:
      {
        nixosModule =
          { ... }:
          {
            system.autoUpgrade = {
              inherit (settings) flake;
              enable = true;
              dates = "02:00";
              randomizedDelaySec = "45min";
            };
          };
      };
  };
}
