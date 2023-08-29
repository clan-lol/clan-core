{ lib
, inputs
, ...
}: {
  imports = [
    ./jsonschema/flake-module.nix
  ];
  flake.lib = import ./default.nix {
    inherit lib;
    inherit (inputs) clan nixpkgs;
  };
}
