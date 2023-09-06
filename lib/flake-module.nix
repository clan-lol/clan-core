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
    inherit self;
    inherit (inputs) nixpkgs;
  };
}
