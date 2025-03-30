{
  lib,
  inputs,
  self,
  ...
}:
let
  inherit (lib)
    filter
    pathExists
    ;
in
rec {
  # We should remove this.
  # It would enforce treating at least 'lib' as a module in a whole
  imports = filter pathExists [
    ./jsonschema/flake-module.nix
    ./inventory/flake-module.nix
    ./build-clan/flake-module.nix
    ./values/flake-module.nix
    ./distributed-service/flake-module.nix
  ];
  flake.clanLib = import ./default.nix {
    inherit lib inputs self;
    inherit (inputs) nixpkgs;
  };
  # TODO: remove this legacy alias
  flake.lib = flake.clanLib;
}
