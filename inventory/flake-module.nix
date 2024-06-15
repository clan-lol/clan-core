{ ... }:
{
  perSystem =
    { pkgs, config, ... }:
    {
      packages.inventory-schema = pkgs.stdenv.mkDerivation {
        name = "inventory-schema";
        src = ./src;

        buildInputs = [ pkgs.cue ];

        installPhase = ''
          mkdir -p $out
        '';
      };
      devShells.inventory-schema = pkgs.mkShell { inputsFrom = [ config.packages.inventory-schema ]; };
    };
}
