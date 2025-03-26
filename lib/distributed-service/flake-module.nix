{ self, inputs, ... }:
let
  inputOverrides = builtins.concatStringsSep " " (
    builtins.map (input: " --override-input ${input} ${inputs.${input}}") (builtins.attrNames inputs)
  );
in
{
  perSystem =
    {
      pkgs,
      lib,
      config,
      system,
      self',
      ...
    }:
    {
      devShells.inventory-schema = pkgs.mkShell {
        inputsFrom = with config.checks; [
          lib-inventory-eval
          self'.devShells.default
        ];
      };

      legacyPackages.schemas = (
        import ./schemas {
          inherit
            pkgs
            self
            lib
            self'
            ;
        }
      );

      # Run: nix-unit --extra-experimental-features flakes --flake .#legacyPackages.x86_64-linux.<attrName>
      legacyPackages.evalTest-distributedServices = import ./tests {
        inherit lib self;
      };

      checks = {
        lib-distributedServices-eval = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"
          export NIX_ABORT_ON_WARN=1
          nix-unit --eval-store "$HOME" \
            --extra-experimental-features flakes \
            ${inputOverrides} \
            --flake ${self}#legacyPackages.${system}.distributedServices

          touch $out
        '';
      };
    };
}
