{
  pkgs,
  lib,
  clanModule,
  clanLib,
}:
let
  eval = lib.evalModules {
    modules = [
      clanModule
    ];
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
