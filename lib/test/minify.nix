# This is a module to reduce the size of the NixOS configuration
# Used by the tests
# It unsets some unnecessary options
{ lib, ... }:
{
  nixpkgs.flake.setFlakeRegistry = false;
  nixpkgs.flake.setNixPath = false;
  nix.registry = lib.mkForce { };
  documentation.doc.enable = false;
  documentation.man.enable = false;
}
