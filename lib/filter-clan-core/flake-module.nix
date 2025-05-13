{ self, ... }:
let
  nixFilter = import ./nix-filter.nix;
in
{
  flake.filter =
    {
      name ? "source",
      include ? [ ],
      exclude ? [ ],
    }:
    nixFilter.filter {
      inherit name exclude;
      include = include ++ [
        "flake.nix"
      ];
      root = self;
    };
}
