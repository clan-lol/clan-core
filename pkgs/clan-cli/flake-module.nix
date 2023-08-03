{ self, ... }: {
  perSystem = { self', pkgs, ... }: {
    devShells.clan = pkgs.callPackage ./shell.nix {
      inherit self;
      inherit (self'.packages) clan;
    };
    packages = {
      clan = pkgs.python3.pkgs.callPackage ./default.nix {
        inherit self;
        zerotierone = self'.packages.zerotierone;
      };
      default = self'.packages.clan;

      ## Optional dependencies for clan cli, we re-expose them here to make sure they all build.
      inherit (pkgs)
        bash
        bubblewrap
        openssh
        sshpass
        zbar
        tor;
      # Override license so that we can build zerotierone without
      # having to re-import nixpkgs.
      zerotierone = pkgs.zerotierone.overrideAttrs (_old: { meta = { }; });
      ## End optional dependencies
    };

    checks = self'.packages.clan.tests // {
      # check if the `clan config` example jsonschema and data is valid
      clan-config-example-schema-valid = pkgs.runCommand "clan-config-example-schema-valid" { } ''
        echo "Checking that example-schema.json is valid"
        ${pkgs.check-jsonschema}/bin/check-jsonschema \
          --check-metaschema ${./.}/tests/config/example-schema.json

        echo "Checking that example-data.json is valid according to example-schema.json"
        ${pkgs.check-jsonschema}/bin/check-jsonschema \
          --schemafile ${./.}/tests/config/example-schema.json \
          ${./.}/tests/config/example-data.json

        touch $out
      '';

      # check if the `clan config` nix jsonschema converter unit tests succeed
      clan-config-nix-unit-tests = pkgs.runCommand "clan-edit-unit-tests" { } ''
        export NIX_PATH=nixpkgs=${pkgs.path}
        ${self'.packages.nix-unit}/bin/nix-unit \
          ${./.}/tests/config/test.nix \
          --eval-store $(realpath .)
        touch $out
      '';
    };
  };

}
