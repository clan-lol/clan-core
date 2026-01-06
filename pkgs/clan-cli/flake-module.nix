{
  inputs,
  self,
  lib,
  ...
}:
{
  imports = [ ./clan_cli/tests/flake-module.nix ];

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
            "modules"
            "nixosModules"
            "flake.lock"
            "templates"
            "clanServices"
            "pkgs/zerotierone"
            "pkgs/minifakeroot"
            "pkgs/clan-cli/clan_cli/tests/flake-module.nix"

            # needed for test_generate_test_vars.py
            "checks/service-dummy-test"
            "checks/flake-module.nix"
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

      # Use fixed ollama on Darwin if available
      ollama = self'.packages.ollama or pkgs.ollama;
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
          inherit (self'.packages) zerotierone minifakeroot;
          inherit ollama;
          templateDerivation = templateDerivation;
          pythonRuntime = pkgs.python3;
          clan-core-path = clanCoreWithVendoredDeps;
          includedRuntimeDeps = [
            "age"
            "git"
            "nix"
          ];
          inherit (self) nixosConfigurations;
        };
        clan-cli-full = pkgs.callPackage ./default.nix {
          inherit (inputs) nixpkgs nix-select;
          inherit (self.legacyPackages.${system}) setupNixInNix;
          inherit (self'.packages) zerotierone minifakeroot;
          inherit ollama;
          clan-core-path = clanCoreWithVendoredDeps;
          templateDerivation = templateDerivation;
          pythonRuntime = pkgs.python3;
          includedRuntimeDeps = lib.importJSON ./clan_lib/nix/allowed-packages.json;
          inherit (self) nixosConfigurations;
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
            existing = "typing.py";
          };
          installPhase = ''
            file1=$existing
            file2=${self'.packages.clan-types}/typing.py

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
