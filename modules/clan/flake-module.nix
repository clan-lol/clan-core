{ self, lib, ... }:
let
  clanModule = lib.modules.importApply ./default.nix { clan-core = self; };
in
{
  flake.modules.clan.default = clanModule;
  perSystem =
    {
      pkgs,
      lib,
      ...
    }:
    let
      jsonDocs = import ./eval-docs.nix {
        inherit
          pkgs
          lib
          clanModule
          ;
        clanLib = self.clanLib;
      };
    in
    {
      legacyPackages.clan-options = jsonDocs.optionsJSON;
    };
}
