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
    system.autoUpgrade = {
      inherit (cfg) flake;
      enable = true;
      dates = "02:00";
      randomizedDelaySec = "45min";
    };
  };
}
