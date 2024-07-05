{ self, inputs, ... }:
let
  inputOverrides = builtins.concatStringsSep " " (
    builtins.map (input: " --override-input ${input} ${inputs.${input}}") (builtins.attrNames inputs)
  );
in
{
  flake.inventory = import ./example.nix { inherit self; };

  perSystem =
    {
      pkgs,
      lib,
      config,
      system,
      self',
      ...
    }:
    let
      buildInventory = import ./build-inventory {
        clan-core = self;
        inherit lib;
      };
    in
    {
      devShells.inventory-schema = pkgs.mkShell {
        inputsFrom = with config.checks; [
          lib-inventory-schema
          lib-inventory-eval
          self'.devShells.default
        ];
      };

      # Run: nix-unit --extra-experimental-features flakes --flake .#legacyPackages.x86_64-linux.evalTests
      legacyPackages.evalTests-inventory = import ./tests {
        inherit buildInventory;
        clan-core = self;
      };

      checks = {
        lib-inventory-eval = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"

          nix-unit --eval-store "$HOME" \
            --extra-experimental-features flakes \
            ${inputOverrides} \
            --flake ${self}#legacyPackages.${system}.evalTests-inventory

          touch $out
        '';

        lib-inventory-schema = pkgs.stdenv.mkDerivation {
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
    };
}
