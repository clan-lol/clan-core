{ lib
, self
, inputs
, ...
}: {
  imports = [
    ./jsonschema/flake-module.nix
  ];
  flake.lib = import ./default.nix {
    clan = self;
    inherit lib;
    inherit (inputs) nixpkgs;
  };
}
