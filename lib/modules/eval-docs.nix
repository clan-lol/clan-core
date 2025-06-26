{
  pkgs,
  lib,
  clanLib,
}:
let
  eval = lib.evalModules {
    modules = [
      clanLib.module
    ];
  };
  evalDocs = pkgs.nixosOptionsDoc {
    options = eval.options;
    warningsAreErrors = false;
  };
in
{
  inherit (evalDocs) optionsJSON optionsNix;
  inherit eval;
}
