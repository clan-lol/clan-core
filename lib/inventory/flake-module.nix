{ self, ... }:
{

  flake.inventory = import ./example.nix { inherit self; };
  perSystem =
    { pkgs, config, ... }:
    {
      devShells.inventory-schema = pkgs.mkShell {
        inputsFrom = [ config.checks.inventory-schema-checks ];
      };

      checks.inventory-schema-checks = pkgs.stdenv.mkDerivation {
        name = "inventory-schema-checks";
        src = ./.;
        buildInputs = [ pkgs.cue ];
        buildPhase = ''
          echo "Running inventory tests..."
          # Cue is easier to run in the same directory as the schema
          cd spec

          echo "Export cue as json-schema..."
          cue export --out openapi root.cue

          echo "Validate test/*.json against inventory-schema..."

          test_dir="../examples"
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
