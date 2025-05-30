{
  _class,
  lib,
  config,
  ...
}:
# Taken from:
# https://github.com/nix-community/srvos/blob/main/nixos/common/nix.nix
{
  imports = lib.optional (_class == "nixos") (
    lib.mkIf config.clan.core.enableRecommendedDefaults {
      nix.daemonCPUSchedPolicy = lib.mkDefault "batch";
      nix.daemonIOSchedClass = lib.mkDefault "idle";
      nix.daemonIOSchedPriority = lib.mkDefault 7;
    }
  );

  config = lib.mkIf config.clan.core.enableRecommendedDefaults {
    # Fallback quickly if substituters are not available.
    nix.settings.connect-timeout = 5;

    # Enable flakes
    nix.settings.experimental-features = [
      "nix-command"
      "flakes"
    ];

    # The default at 10 is rarely enough.
    nix.settings.log-lines = lib.mkDefault 25;

    # Avoid disk full issues
    nix.settings.max-free = lib.mkDefault (3000 * 1024 * 1024);
    nix.settings.min-free = lib.mkDefault (512 * 1024 * 1024);

    # Avoid copying unnecessary stuff over SSH
    nix.settings.builders-use-substitutes = true;
  };
}
