{
  perSystem =
    { pkgs, ... }:
    {
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
        lib-jsonschema-nix-unit-tests = pkgs.runCommand "lib-jsonschema-nix-unit-tests" { } ''
          export NIX_PATH=nixpkgs=${pkgs.path}
          ${pkgs.nix-unit}/bin/nix-unit \
            ${./.}/test.nix \
            --eval-store $(realpath .) \
            --show-trace
          touch $out
        '';
      };
    };
}
