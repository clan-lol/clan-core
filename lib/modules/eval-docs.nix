{
  pkgs,
  lib,
  clanLib,
}:
let
  eval = lib.evalModules {
    # TODO: Move this into a 'classForMachines' or something
    # @enzime why do we need this here?
    class = "nixos";
    modules = [
      clanLib.buildClanModule.flakePartsModule
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
