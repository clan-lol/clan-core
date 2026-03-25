{
  lib,
  inputs,
  self,
  ...
}:
let
  inputOverrides = self.clanLib.flake-inputs.getOverrides inputs;
in
{
  perSystem =
    { pkgs, system, ... }:
    {
      legacyPackages.evalTests-lib-jsonschema-unit-tests = import ./test.nix {
        inherit lib;
        inherit (self) clanLib;
      };

      checks = {
        # check if the `clan config` example jsonschema and data is valid
        lib-jsonschema-example-valid = pkgs.runCommand "lib-jsonschema-example-valid" { } ''
          echo "Checking that example-schema.json is valid"
          ${pkgs.check-jsonschema}/bin/check-jsonschema \
            --check-metaschema ${./.}/example-schema.json

          echo "Checking that example-data.json is valid according to example-schema.json"
          ${pkgs.check-jsonschema}/bin/check-jsonschema \
            --schemafile ${./.}/example-schema.json \
            ${./.}/example-data.json

          touch $out
        '';
      };

      # Run: nix build .#legacyPackages.x86_64-linux.evalCheck-lib-jsonschema-unit-tests
      legacyPackages.evalCheck-lib-jsonschema-unit-tests = self.clanLib.test.mkEvalCheck {
        inherit pkgs system inputOverrides;
        name = "lib-jsonschema-unit-tests";
        flakeAttr = "${
          self.filter {
            include = [
              "flake.nix"
              "lib"
              "flakeModules"
            ];
          }
        }#legacyPackages.${system}.evalTests-lib-jsonschema-unit-tests";
      };
    };
}
