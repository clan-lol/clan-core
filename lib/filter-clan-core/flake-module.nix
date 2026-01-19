{ self, lib, ... }:
let
  nixFilter = import ./nix-filter.nix;
in
{
  flake.filter =
    {
      name ? "source",
      include ? null,
      exclude ? null,
    }:
    nixFilter.filter (
      {
        inherit name;
        root = self;
      }
      // (lib.optionalAttrs (include != null) { include = include; })
      // (lib.optionalAttrs (exclude != null) { exclude = exclude; })
    );
}
