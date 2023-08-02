# tests for the nixos options to jsonschema converter
# run these tests via `nix-unit ./test.nix`
{ lib ? (import <nixpkgs> { }).lib
, slib ? import ../../clan_cli/config/schema-lib.nix { inherit lib; }
}:
let
  evaledOptions =
    let
      evaledConfig = lib.evalModules {
        modules = [ ./example-interface.nix ];
      };
    in
    evaledConfig.options;
in
{
  testParseOptions = {
    expr = slib.parseOptions evaledOptions;
    expected = builtins.fromJSON (builtins.readFile ./example-schema.json);
  };
}
