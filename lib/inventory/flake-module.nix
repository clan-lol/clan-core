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

      optionsFromModule =
        mName:
        let
          eval = self.lib.evalClanModules [ mName ];
        in
        if (eval.options.clan ? "${mName}") then eval.options.clan.${mName} else { };

      modulesSchema = lib.mapAttrs (
        moduleName: _: jsonLib'.parseOptions (optionsFromModule moduleName) { }
      ) self.clanModules;

      jsonLib = self.lib.jsonschema {
        # includeDefaults = false;
      };
      jsonLib' = self.lib.jsonschema {
        # includeDefaults = false;
        header = { };
      };
      inventorySchema = jsonLib.parseModule (import ./build-inventory/interface.nix);

      getRoles =
        modulePath:
        let
          rolesDir = "${modulePath}/roles";
        in
        if builtins.pathExists rolesDir then
          lib.pipe rolesDir [
            builtins.readDir
            (lib.filterAttrs (_n: v: v == "regular"))
            lib.attrNames
            (map (fileName: lib.removeSuffix ".nix" fileName))
          ]
        else
          null;

      schema = inventorySchema // {
        properties = inventorySchema.properties // {
          services = {
            type = "object";
            additionalProperties = false;
            properties = lib.mapAttrs (moduleName: moduleSchema: {
              type = "object";
              additionalProperties = {
                type = "object";
                additionalProperties = false;
                properties = {
                  meta =
                    inventorySchema.properties.services.additionalProperties.additionalProperties.properties.meta;
                  config = moduleSchema;
                  roles = {
                    type = "object";
                    additionalProperties = false;
                    required = [ ];
                    properties = lib.listToAttrs (
                      map
                        (role: {
                          name = role;
                          value =
                            inventorySchema.properties.services.additionalProperties.additionalProperties.properties.roles.additionalProperties;
                        })
                        (
                          let
                            roles = getRoles self.clanModules.${moduleName};
                          in
                          if roles == null then [ ] else roles
                        )
                    );
                  };
                  machines =
                    lib.recursiveUpdate
                      inventorySchema.properties.services.additionalProperties.additionalProperties.properties.machines
                      { additionalProperties.properties.config = moduleSchema; };
                };
              };
            }) modulesSchema;
          };
        };
      };
    in
    {
      legacyPackages.inventorySchema = schema;

      devShells.inventory-schema = pkgs.mkShell {
        inputsFrom = with config.checks; [
          lib-inventory-examples-cue
          lib-inventory-eval
          self'.devShells.default
        ];
      };

      # Inventory schema with concrete module implementations
      packages.inventory-schema = pkgs.stdenv.mkDerivation {
        name = "inventory-schema";
        buildInputs = [ pkgs.cue ];
        src = ./.;
        buildPhase = ''
          export SCHEMA=${builtins.toFile "inventory-schema.json" (builtins.toJSON self'.legacyPackages.inventorySchema)}
          cp $SCHEMA schema.json
          cue import -f -p compose -l '#Root:' schema.json
          mkdir $out
          cp schema.cue $out
          cp schema.json $out
        '';
      };

      # Run: nix-unit --extra-experimental-features flakes --flake .#legacyPackages.x86_64-linux.evalTests
      legacyPackages.evalTests-inventory = import ./tests {
        inherit buildInventory;
        clan-core = self;
      };

      checks = {
        lib-inventory-examples-cue = pkgs.stdenv.mkDerivation {
          name = "inventory-schema-checks";
          src = ./.;
          buildInputs = [ pkgs.cue ];
          buildPhase = ''
            echo "Running inventory tests..."
            # Cue is easier to run in the same directory as the schema
            cp ${self'.packages.inventory-schema}/schema.cue root.cue

            ls -la .

            echo "Validate test/*.json against inventory-schema..."
            cat root.cue

            test_dir="./examples"
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
        lib-inventory-eval = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"

          nix-unit --eval-store "$HOME" \
            --extra-experimental-features flakes \
            ${inputOverrides} \
            --flake ${self}#legacyPackages.${system}.evalTests-inventory

          touch $out
        '';
      };
    };
}
