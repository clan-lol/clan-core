{
  pkgs,
  lib,
  clan-core,
}:
let
  eval = lib.evalModules {
    modules = [
      clan-core.modules.clan.default
    ];
  };

  evalDocs = pkgs.nixosOptionsDoc {
    options = eval.options;
    warningsAreErrors = false;
    transformOptions = clan-core.clanLib.docs.stripStorePathsFromDeclarations;
  };
in
{
  inherit (evalDocs) optionsJSON optionsNix;
  inherit eval;
}
