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

        # check if the `clan config` nix jsonschema converter unit tests succeed
        lib-jsonschema-unit-tests =
          pkgs.runCommand "lib-jsonschema-unit-tests" { nativeBuildInputs = [ pkgs.nix-unit ]; }
            ''
              HOME=$(realpath .)

              nix-unit --eval-store "$HOME" \
                --extra-experimental-features flakes \
                --show-trace \
                ${inputOverrides} \
                --flake ${
                  self.filter {
                    include = [
                      "lib"
                      "flakeModules"
                    ];
                  }
                }#legacyPackages.${system}.evalTests-lib-jsonschema-unit-tests

              touch $out
            '';
      };
    };
}
