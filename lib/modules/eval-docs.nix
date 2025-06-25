{
  pkgs,
  lib,
  clanLib,
}:
let
  eval = lib.evalModules {
    class = "nixos";
    modules = [
      (lib.modules.importApply ./clan/interface.nix { inherit clanLib; })
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
