{ pkgs, lib }:
let
  eval = lib.evalModules {
    class = "nixos";
    modules = [
      ./interface.nix
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
