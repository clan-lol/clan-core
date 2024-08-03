{
  lib,
  nixpkgs,
  clan-core,
  specialArgs ? { },
}:
# Returns a function that takes self, which should point to the directory of the flake
{ self }:
module:
(lib.evalModules {
  specialArgs = {
    inherit self clan-core nixpkgs;
  } // specialArgs;
  modules = [
    ./interface.nix
    module
  ];
}).config
