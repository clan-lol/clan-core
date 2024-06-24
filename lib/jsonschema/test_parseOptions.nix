# tests for the nixos options to jsonschema converter
# run these tests via `nix-unit ./test.nix`
{
  lib ? (import <nixpkgs> { }).lib,
  slib ? import ./. { inherit lib; },
}:
{
  testParseOptions = {
    expr = slib.parseModule ./example-interface.nix;
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
