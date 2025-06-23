{
  lib,
  inputs,
  self,
  ...
}:
rec {
  # TODO: automatically generate this from the directory conventions
  imports = [
    ./modules/flake-module.nix
    ./clanTest/flake-module.nix
    ./introspection/flake-module.nix
    ./inventory/flake-module.nix
    ./jsonschema/flake-module.nix
    ./types/flake-module.nix
  ];
  flake.clanLib = import ./default.nix {
    inherit lib inputs self;
    inherit (inputs) nixpkgs nix-darwin;
  };
  # TODO: remove this legacy alias
  flake.lib = flake.clanLib;
}
