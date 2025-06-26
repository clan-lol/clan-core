{
  lib,
  nixpkgs,
  nix-darwin ? null,
  clan-core,
  self,
  specialArgs ? { },
}:
# Returns a function that takes self, which should point to the directory of the flake
module:
(lib.evalModules {
  specialArgs = {
    inherit (clan-core) clanLib;
    inherit
      self
      clan-core
      nixpkgs
      nix-darwin
      ;
  };
  modules = [
    ./clan/default.nix
    module
    {
      inherit specialArgs;
    }
  ];
}).config
