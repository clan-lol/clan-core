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
    inherit
      self
      clan-core
      nixpkgs
      nix-darwin
      ;
  };
  modules = [
    (lib.modules.importApply ./clan/interface.nix { inherit (clan-core) clanLib; })
    module
    {
      inherit specialArgs;
    }
  ];
}).config
