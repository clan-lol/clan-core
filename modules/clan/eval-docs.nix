{
  pkgs,
  lib,
  clanModule,
  clanLib,
  clan-core,
}:
let
  eval = lib.evalModules {
    modules = [
      clanModule
    ];
    specialArgs = {
      self = clan-core;
    };
  };

  evalDocs = pkgs.nixosOptionsDoc {
    options = eval.options;
    warningsAreErrors = false;
    transformOptions = clanLib.docs.stripStorePathsFromDeclarations;
  };
in
{
  inherit (evalDocs) optionsJSON optionsNix;
  inherit eval;
}
