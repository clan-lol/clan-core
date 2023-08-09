{ lib
, ...
}: {
  imports = [
    ./jsonschema/flake-module.nix
  ];
  flake.lib = import ./default.nix { inherit lib; };
}
