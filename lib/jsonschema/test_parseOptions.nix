# tests for the nixos options to jsonschema converter
# run these tests via `nix-unit ./test.nix`
{
  lib ? (import <nixpkgs> { }).lib,
  slib ? import ./. { inherit lib; },
}:
let
  evaledOptions =
    let
      evaledConfig = lib.evalModules { modules = [ ./example-interface.nix ]; };
    in
    evaledConfig.options;
in
{
  testParseOptions = {
    expr = slib.parseOptions evaledOptions;
    expected = builtins.fromJSON (builtins.readFile ./example-schema.json);
  };

  testParseNestedOptions =
    let
      evaled = lib.evalModules {
        modules = [ { options.foo.bar = lib.mkOption { type = lib.types.bool; }; } ];
      };
    in
    {
      expr = slib.parseOptions evaled.options;
      expected = {
        additionalProperties = false;
        properties = {
          foo = {
            additionalProperties = false;
            properties = {
              bar = {
                type = "boolean";
              };
            };
            required = [ "bar" ];
            type = "object";
          };
        };
        type = "object";
      };
    };
}
