# ============================================================================ #
#
# Aggregates configs making them available to `default.nix', `flake.nix',
# or other projects that want to consume this module/package as a dependency.
#
# ---------------------------------------------------------------------------- #
{
  _file = "theme/nix/floco-cfg.nix";
  imports =
    let
      ifExist = builtins.filter builtins.pathExists [
        ./pdefs.nix # Generated `pdefs.nix'
        ./foverrides.nix # Explicit config
      ];
    in
    ifExist
    ++ [

    ];
}
# ---------------------------------------------------------------------------- #
#
#
#
# ============================================================================ #

