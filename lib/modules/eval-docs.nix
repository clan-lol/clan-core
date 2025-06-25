{
  pkgs,
  lib,
  clanLib,
}:
let
  eval = lib.evalModules {
    class = "nixos";
    modules = [
      (import ./clan/default.nix { inherit clanLib; })
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
