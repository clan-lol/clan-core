{
  self,
  lib,
  pkgs,
  flakeOptions,
  ...
}:
let
  jsonLib = self.clanLib.jsonschema { inherit includeDefaults; };
  includeDefaults = true;

  opts = (flakeOptions.flake.type.getSubOptions [ "flake" ]);
  clanOpts = opts.clan.type.getSubOptions [ "clan" ];
  include = [
    "directory"
    "inventory"
    "machines"
    "meta"
    "modules"
    "outputs"
    "secrets"
    "templates"
  ];
  clanSchema = jsonLib.parseOptions (lib.filterAttrs (n: _v: lib.elem n include) clanOpts) { };

  clan-schema-abstract = pkgs.stdenv.mkDerivation {
    name = "clan-schema-files";
    buildInputs = [ pkgs.cue ];
    src = ./.;
    buildPhase = ''
      export SCHEMA=${builtins.toFile "clan-schema.json" (builtins.toJSON clanSchema)}
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
    flakeOptions
    clanSchema
    clan-schema-abstract
    ;
}
