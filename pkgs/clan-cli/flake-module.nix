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
          ];
        };
      };

      # We need to add the paths of the templates to the nix store such that they are available
      # only adding clanCoreWithVendoredDeps to the nix store is not enough
      templateDerivation = pkgs.closureInfo {
        rootPaths =
          builtins.attrValues (self.clanLib.select "clan.templates.clan.*.path" self)
          ++ builtins.attrValues (self.clanLib.select "clan.templates.machine.*.path" self);
      };
    in
    {
      devShells.clan-cli = pkgs.callPackage ./shell.nix {
        inherit (self'.packages) clan-cli;
        inherit self';
        inherit (inputs) nix-select;
      };
      packages = {
        clan-cli = pkgs.callPackage ./default.nix {
          inherit (inputs) nixpkgs nix-select;
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
          clan-core-path = clanCoreWithVendoredDeps;
          templateDerivation = templateDerivation;
          pythonRuntime = pkgs.python3;
          includedRuntimeDeps = lib.importJSON ./clan_cli/nix/allowed-packages.json;
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

            # Retrieve python API Typescript types
            # delete the reserved tags from typechecking because the conversion library doesn't support them
            jq 'del(.properties.tags.properties)' ${self'.legacyPackages.schemas.inventory}/schema.json > schema.json
            json2ts --input schema.json > $out/Inventory.ts
            cp ${self'.legacyPackages.schemas.inventory}/* $out
          '';
        };

        default = self'.packages.clan-cli;
      };

      checks = self'.packages.clan-cli.tests // {
        inventory-classes-up-to-date = pkgs.stdenv.mkDerivation {
          name = "inventory-classes-up-to-date";
          src = ./clan_cli/inventory;

          env = {
            classFile = "classes.py";
          };
          installPhase = ''
            ${self'.packages.classgen}/bin/classgen ${self'.legacyPackages.schemas.inventory-schema-abstract}/schema.json b_classes.py
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
