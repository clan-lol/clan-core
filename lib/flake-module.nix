{ lib
, ...
}: {
  flake.lib = import ./default.nix { inherit lib; };
}
