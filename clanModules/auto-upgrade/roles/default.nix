{
  config,
  lib,
  ...
}:
let
  cfg = config.clan.auto-upgrade;
in
{
  options.clan.auto-upgrade = {
    flake = lib.mkOption {
      type = lib.types.str;
      description = "Flake reference";
    };
  };

  config = {

    warnings = [
      "The clan.auto-upgrade module is deprecated and will be removed on 2025-07-15.
      Please migrate to user-maintained configuration or the new equivalent clan services
      (https://docs.clan.lol/reference/clanServices)."
    ];

    system.autoUpgrade = {
      inherit (cfg) flake;
      enable = true;
      dates = "02:00";
      randomizedDelaySec = "45min";
    };
  };
}
