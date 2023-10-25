{ lib
, inputs
, self
, ...
}: {
  imports = [
    ./jsonschema/flake-module.nix
  ];
  flake.lib = import ./default.nix {
    inherit lib;
    inherit (inputs) nixpkgs;
    clan-core = self;
  };
}
