{
  inputs,
  self,
  lib,
  ...
}:
{
  perSystem =
    {
      self',
      pkgs,
      system,
      ...
    }:
    let
      clanCoreWithVendoredDeps = self'.packages.clan-core-flake.override {
        clanCore = self.filter {
          include = [
            "clanModules"
            "flakeModules"
            "lib"
            "nixosModules"
            "flake.lock"
            "templates"
            "clanServices"
          ];
        };
      };

      # We need to add the paths of the templates to the nix store such that they are available
      # only adding clanCoreWithVendoredDeps to the nix store is not enough
      templateDerivation = pkgs.closureInfo {
        rootPaths =
          builtins.attrValues (self.inputs.nix-select.lib.select "clan.templates.clan.*.path" self)
          ++ builtins.attrValues (self.inputs.nix-select.lib.select "clan.templates.machine.*.path" self);
      };
    in
    {
      devShells.clan-cli = pkgs.callPackage ./shell.nix {
        inherit self' self;
        inherit (self'.packages) clan-cli;
      };
      packages = {
        clan-cli = pkgs.callPackage ./default.nix {
          inherit (inputs) nixpkgs nix-select;
          inherit (self.legacyPackages.${system}) setupNixInNix;
          templateDerivation = templateDerivation;
          pythonRuntime = pkgs.python3;
          clan-core-path = clanCoreWithVendoredDeps;
          includedRuntimeDeps = [
            "age"
            "git"
          ];
        };
        clan-cli-full = pkgs.callPackage ./default.nix {
          inherit (inputs) nixpkgs nix-select;
          inherit (self.legacyPackages.${system}) setupNixInNix;
          clan-core-path = clanCoreWithVendoredDeps;
          templateDerivation = templateDerivation;
          pythonRuntime = pkgs.python3;
          includedRuntimeDeps = lib.importJSON ./clan_lib/nix/allowed-packages.json;
        };
        clan-cli-docs = pkgs.stdenv.mkDerivation {
          name = "clan-cli-docs";
          src = ./.;

          buildInputs = [
            # TODO: see postFixup clan-cli/default.nix:L188
            pkgs.python3
            self'.packages.clan-cli.propagatedBuildInputs
          ];

          installPhase = ''
            python docs.py reference
            mkdir -p $out
            cp -r out/* $out
            ls -lah $out
          '';
        };
        clan-ts-api = pkgs.stdenv.mkDerivation {
          name = "clan-ts-api";
          src = ./.;

          buildInputs = [
            pkgs.python3
            pkgs.json2ts
            pkgs.jq
          ];

          installPhase = ''
            mkdir -p $out
            # Retrieve python API Typescript types
            python api.py > $out/API.json
            json2ts --input $out/API.json > $out/API.ts
            # Substitute '{}' with 'Record<string, never>' because typescript is like that
            # It treats it not as the type of an empty object, but as non-nullish.
            # Should be fixed in json2ts: https://github.com/bcherny/json-schema-to-typescript/issues/557
            sed -i -e 's/{}/Record<string, never>/g' $out/API.ts
          '';
        };
        clan-lib-openapi = pkgs.stdenv.mkDerivation {
          name = "clan-lib-openapi";
          src = ./.;

          buildInputs = [
            pkgs.python3
          ];

          installPhase = ''
            export INPUT_PATH=${self'.packages.clan-ts-api}/API.json
            python openapi.py
            cp openapi.json $out
          '';
        };

        default = self'.packages.clan-cli;
      };

      checks = self'.packages.clan-cli.tests // {
        inventory-classes-up-to-date = pkgs.stdenv.mkDerivation {
          name = "inventory-classes-up-to-date";
          src = ./clan_lib/nix_models;

          env = {
            classFile = "clan.py";
          };
          installPhase = ''
            ${self'.packages.classgen}/bin/classgen ${self'.legacyPackages.schemas.clan-schema-abstract}/schema.json b_classes.py
            file1=$classFile
            file2=b_classes.py

            echo "Comparing $file1 and $file2"
            if cmp -s "$file1" "$file2"; then
                echo "Files are identical"
                echo "Classes file is up to date"
            else
                echo "Classes file is out of date or has been modified"
                echo "run 'direnv reload' in the pkgs/clan-cli directory to refresh the classes file"
                echo "--------------------------------\n"
                diff "$file1" "$file2"
                echo "--------------------------------\n\n"
                exit 1
            fi

            touch $out
          '';
        };
      };
    };
}
