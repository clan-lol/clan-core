{
  self,
  self',
  pkgs,
  ...
}:
let

  modulesSchema = self.clanLib.modules.getModulesSchema {
    modules = self.clanModules;
    inherit pkgs;
    clan-core = self;
  };

  jsonLib = self.clanLib.jsonschema { inherit includeDefaults; };
  includeDefaults = true;

  frontMatterSchema = jsonLib.parseOptions self.clanLib.modules.frontmatterOptions { };

  inventorySchema = jsonLib.parseModule (
    import ../build-inventory/interface.nix { inherit (self) clanLib; }
  );

  renderSchema = pkgs.writers.writePython3Bin "render-schema" {
    flakeIgnore = [
      "F401"
      "E501"
    ];
  } ./render_schema.py;

  inventory-schema-abstract = pkgs.stdenv.mkDerivation {
    name = "inventory-schema-files";
    buildInputs = [ pkgs.cue ];
    src = ./.;
    buildPhase = ''
      export SCHEMA=${builtins.toFile "inventory-schema.json" (builtins.toJSON inventorySchema)}
      cp $SCHEMA schema.json
      # Also generate a CUE schema version that is derived from the JSON schema
      cue import -f -p compose -l '#Root:' schema.json
      mkdir $out
      cp schema.cue $out
      cp schema.json $out
    '';
  };
in
{
  inherit
    frontMatterSchema
    inventorySchema
    modulesSchema
    renderSchema
    inventory-schema-abstract
    ;

  # Inventory schema, with the modules schema added per role
  inventory =
    pkgs.runCommand "rendered"
      {
        buildInputs = [
          pkgs.python3
          self'.packages.clan-cli
        ];
      }
      ''
        export INVENTORY_SCHEMA_PATH=${builtins.toFile "inventory-schema.json" (builtins.toJSON inventorySchema)}
        export MODULES_SCHEMA_PATH=${builtins.toFile "modules-schema.json" (builtins.toJSON modulesSchema)}

        mkdir $out
        # The python script will place the schemas in the output directory
        exec python3 ${renderSchema}/bin/render-schema
      '';
}
