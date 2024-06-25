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

      checks.inventory-schema-checks = pkgs.stdenv.mkDerivation {
        name = "inventory-schema-checks";
        src = ./src;
        buildInputs = [ pkgs.cue ];
        buildPhase = ''
          echo "Running inventory tests..."

          echo "Export cue as json-schema..."
          cue export --out openapi root.cue

          echo "Validate test/*.json against inventory-schema..."

          test_dir="test"
          for file in "$test_dir"/*; do
            # Check if the item is a file
            if [ -f "$file" ]; then
              # Print the filename
              echo "Running test on: $file"

              # Run the cue vet command
              cue vet "$file" root.cue -d "#Root"
            fi
          done

          touch $out
        '';
      };
    };
}
