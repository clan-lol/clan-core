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
      flakeLock = lib.importJSON (clanCore + "/flake.lock");
      flakeInputs = builtins.removeAttrs inputs [ "self" ];
      flakeLockVendoredDeps =
        flakeLock:
        flakeLock
        // {
          nodes =
            flakeLock.nodes
            // (lib.flip lib.mapAttrs flakeInputs (
              name: _:
              # remove follows and let 'nix flake lock' re-compute it later
              # (lib.removeAttrs flakeLock.nodes.${name} ["inputs"])
              flakeLock.nodes.${name}
              // {
                locked = {
                  inherit (flakeLock.nodes.${name}.locked) narHash;
                  lastModified =
                    # lol, nixpkgs has a different timestamp on the fs???
                    if name == "nixpkgs" then 0 else 1;
                  path = "${inputs.${name}}";
                  type = "path";
                };
              }
            ));
        };
      clanCoreLock = flakeLockVendoredDeps flakeLock;
      clanCoreLockFile = builtins.toFile "clan-core-flake.lock" (builtins.toJSON clanCoreLock);

      clanCoreNode = {

        inputs = lib.mapAttrs (name: _input: name) flakeInputs;
        locked = {
          lastModified = 1;
          path = "${clanCore}";
          type = "path";
        };
        original = {
          type = "tarball";
          url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
        };
      };
      # generate a lock file that nix will accept for our flake templates,
      # in order to not require internet access during tests.
      templateLock = clanCoreLock // {
        nodes = clanCoreLock.nodes // {
          clan-core = clanCoreNode;
          nixpkgs-lib = clanCoreLock.nodes.nixpkgs; # required by flake-parts
          flake-parts = clanCoreLock.nodes.flake-parts;
          root = clanCoreLock.nodes.root // {
            inputs = clanCoreLock.nodes.root.inputs // {
              clan-core = "clan-core";
              nixpkgs = "nixpkgs";
              clan = "clan-core";
              flake-parts = "flake-parts";
            };
          };
        };
      };
      templateLockFile = builtins.toFile "template-flake.lock" (builtins.toJSON templateLock);

      # We need to add the paths of the templates to the nix store such that they are available
      # only adding clanCoreWithVendoredDeps to the nix store is not enough
      templateDerivation = pkgs.closureInfo {
        rootPaths =
          builtins.attrValues (self.clanLib.select "clan.templates.clan.*.path" self)
          ++ builtins.attrValues (self.clanLib.select "clan.templates.machine.*.path" self);
      };

      clanCoreWithVendoredDeps =
        pkgs.runCommand "clan-core-with-vendored-deps"
          {
            buildInputs = [
              pkgs.findutils
              pkgs.git
              pkgs.jq
              pkgs.nix
            ];
          }
          ''
            set -e
            export HOME=$(realpath .)
            export NIX_STATE_DIR=$HOME
            export NIX_STORE_DIR=$HOME
            cp -r ${clanCore} $out
            chmod +w -R $out
            cp ${clanCoreLockFile} $out/flake.lock
            nix flake lock $out --extra-experimental-features 'nix-command flakes'
            clanCoreHash=$(nix hash path ${clanCore} --extra-experimental-features 'nix-command')

            ## ==> We need this to make nix flake update work on the templates
            ## however then we have to re-add the clan templates to the nix store
            ## which is not possible (or I don't know how)
            # for templateDir in $(find $out/templates/clan -mindepth 1 -maxdepth 1 -type d); do
            #   if ! [ -e "$templateDir/flake.nix" ]; then
            #     continue
            #   fi
            #   cp ${templateLockFile} $templateDir/flake.lock
            #   cat $templateDir/flake.lock | jq ".nodes.\"clan-core\".locked.narHash = \"$clanCoreHash\"" > $templateDir/flake.lock.final
            #   mv $templateDir/flake.lock.final $templateDir/flake.lock
            #   nix flake lock $templateDir --extra-experimental-features 'nix-command flakes'
            # done
          '';
    in
    {
      devShells.clan-cli = pkgs.callPackage ./shell.nix {
        inherit (self'.packages) clan-cli clan-cli-full;
        inherit self';
      };
      packages = {
        clan-cli = pkgs.callPackage ./default.nix {
          inherit (inputs) nixpkgs;
          templateDerivation = templateDerivation;
          pythonRuntime = pkgs.python3;
          clan-core-path = clanCoreWithVendoredDeps;
          includedRuntimeDeps = [
            "age"
            "git"
          ];
        };
        clan-cli-full = pkgs.callPackage ./default.nix {
          inherit (inputs) nixpkgs;
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
