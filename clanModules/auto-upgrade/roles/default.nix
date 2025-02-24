{
  config,
  lib,
  ...
}:
let
  cfg = config.clan.autoUpgrade;
in
{
  options.clan.autoUpgrade = {
    flake = lib.mkOption {
      type = lib.types.str;
      description = "Flake reference";
    };
  };
  config = {
    system.autoUpgrade = {
      inherit (cfg.clan.autoUpgrade) flake;
      enable = true;
      dates = "02:00";
      randomizedDelaySec = "45min";
    };
  };
}
