# tests for the nixos options to jsonschema converter
# run these tests via `nix-unit ./test.nix`
{
  lib ? (import <nixpkgs> { }).lib,
  slib ? (import ./. { inherit lib; } { }),
}:
let
  description = "Test Description";

  # Wrap the parseOption function to reduce the surface that needs to be migrated, when '$exportedModuleInfo' changes
  parseOption = opt: filterSchema (slib.parseOption opt);

  evalType =
    type: default:
    (evalModuleOptions {
      options.opt = lib.mkOption {
        inherit type description;
        default = default;
      };
    }).opt;

  evalModuleOptions =
    module:
    let
      evaledConfig = lib.evalModules {
        modules = [
          module
        ];
      };
    in
    evaledConfig.options;

  filterSchema =
    schema: lib.filterAttrsRecursive (name: _value: name != "$exportedModuleInfo") schema;
in
{
  testNoDefaultNoDescription =
    let
      evaledConfig = lib.evalModules {
        modules = [ { options.opt = lib.mkOption { type = lib.types.bool; }; } ];
      };
    in
    {
      expr = parseOption evaledConfig.options.opt;
      expected = {
        type = "boolean";
      };
    };

  testDescriptionIsAttrs =
    let
      evaledConfig = lib.evalModules {
        modules = [
          {
            options.opt = lib.mkOption {
              type = lib.types.bool;
              description = {
                _type = "mdDoc";
                text = description;
              };
            };
          }
        ];
      };
    in
    {
      expr = parseOption evaledConfig.options.opt;
      expected = {
        type = "boolean";
        inherit description;
      };
    };

  testBool =
    let
      default = false;
    in
    {
      expr = parseOption (evalType lib.types.bool default);
      expected = {
        type = "boolean";
        inherit default description;
      };
    };

  testString =
    let
      default = "hello";
    in
    {
      expr = parseOption (evalType lib.types.str default);
      expected = {
        type = "string";
        inherit default description;
      };
    };

  testInteger =
    let
      default = 42;
    in
    {
      expr = parseOption (evalType lib.types.int default);
      expected = {
        type = "integer";
        inherit default description;
      };
    };

  testFloat =
    let
      default = 42.42;
    in
    {
      expr = parseOption (evalType lib.types.float default);
      expected = {
        type = "number";
        inherit default description;
      };
    };

  testEnum =
    let
      default = "foo";
      values = [
        "foo"
        "bar"
        "baz"
      ];
    in
    {
      expr = parseOption (evalType (lib.types.enum values) default);
      expected = {
        enum = values;
        inherit default description;
      };
    };

  testListOfInt =
    let
      default = [
        1
        2
        3
      ];
    in
    {
      expr = parseOption (evalType (lib.types.listOf lib.types.int) default);
      expected = {
        type = "array";
        items = {
          type = "integer";
        };
        inherit default description;
      };
    };

  testListOfUnspecified =
    let
      default = [
        1
        2
        3
      ];
    in
    {
      expr = parseOption (evalType (lib.types.listOf lib.types.unspecified) default);
      expected = {
        type = "array";
        items = {
          type = [
            "boolean"
            "integer"
            "number"
            "string"
            "array"
            "object"
            "null"
          ];
        };
        inherit default description;
      };
    };

  testAttrs =
    let
      default = {
        foo = 1;
        bar = 2;
        baz = 3;
      };
    in
    {
      expr = parseOption (evalType (lib.types.attrs) default);
      expected = {
        type = "object";
        additionalProperties = true;
        inherit default description;
      };
    };

  testAttrsOfInt =
    let
      default = {
        foo = 1;
        bar = 2;
        baz = 3;
      };
    in
    {
      expr = parseOption (evalType (lib.types.attrsOf lib.types.int) default);
      expected = {
        type = "object";
        additionalProperties = {

          type = "integer";
        };
        inherit default description;
      };
    };

  testLazyAttrsOfInt =
    let
      default = {
        foo = 1;
        bar = 2;
        baz = 3;
      };
    in
    {
      expr = parseOption (evalType (lib.types.lazyAttrsOf lib.types.int) default);
      expected = {
        type = "object";
        additionalProperties = {

          type = "integer";
        };
        inherit default description;
      };
    };

  testNullOrBool =
    let
      default = null; # null is a valid value for this type
    in
    {
      expr = parseOption (evalType (lib.types.nullOr lib.types.bool) default);
      expected = {
        oneOf = [
          { type = "null"; }
          {
            type = "boolean";
            "$exportedModuleInfo" = {
              path = [ "opt" ];
              default = null;
              defaultText = null;
              required = true;
            };
          }
        ];
        inherit default description;
      };
    };

  testNullOrNullOr =
    let
      default = null; # null is a valid value for this type
    in
    {
      expr = parseOption (evalType (lib.types.nullOr (lib.types.nullOr lib.types.bool)) default);
      expected = {
        oneOf = [
          { type = "null"; }
          {
            "$exportedModuleInfo" = {
              default = null;
              defaultText = null;
              path = [ "opt" ];
              required = true;
            };
            oneOf = [
              { type = "null"; }
              {
                "$exportedModuleInfo" = {
                  default = null;
                  defaultText = null;
                  path = [ "opt" ];
                  required = true;
                };
                type = "boolean";
              }
            ];
          }
        ];
        inherit default description;
      };
    };

  testSubmoduleOption =
    let
      subModule = {
        options.opt = lib.mkOption {
          type = lib.types.bool;
          default = true;
          inherit description;
        };
      };
    in
    {
      expr = parseOption (evalType (lib.types.submodule subModule) { });
      expected = {
        type = "object";
        additionalProperties = false;
        description = "Test Description";
        properties = {
          opt = {
            type = "boolean";
            default = true;
            inherit description;
          };
        };
        required = [ ];
        default = { };
      };
    };

  testSubmoduleOptionWithoutDefault =
    let
      subModule = {
        options.foo = lib.mkOption {
          type = lib.types.bool;
          inherit description;
        };
      };
      opt = evalType (lib.types.submodule subModule) { };
    in
    {
      inherit opt;
      expr = parseOption (opt);
      expected = {
        type = "object";
        additionalProperties = false;
        description = "Test Description";
        properties = {
          foo = {
            type = "boolean";
            inherit description;
          };
        };
        default = { };
        required = [ "foo" ];
      };
    };

  testAttrsOfSubmodule =
    let
      subModule = {
        options.opt = lib.mkOption {
          type = lib.types.bool;
          default = true;
          inherit description;
        };
      };
      default = {
        foo.opt = false;
        bar.opt = true;
      };
    in
    {
      expr = parseOption (evalType (lib.types.attrsOf (lib.types.submodule subModule)) default);
      expected = {
        type = "object";
        additionalProperties = {

          type = "object";
          additionalProperties = false;
          properties = {
            opt = {
              type = "boolean";
              default = true;
              inherit description;
            };
          };
          required = [ ];
        };
        inherit default description;
      };
    };

  testListOfSubmodule =
    let
      subModule = {
        options.opt = lib.mkOption {
          type = lib.types.bool;
          default = true;
          inherit description;
        };
      };
      default = [
        { opt = false; }
        { opt = true; }
      ];
    in
    {
      expr = parseOption (evalType (lib.types.listOf (lib.types.submodule subModule)) default);
      expected = {
        type = "array";
        items = {
          type = "object";
          additionalProperties = false;
          properties = {
            opt = {
              type = "boolean";
              default = true;
              inherit description;
            };
          };
          required = [ ];
        };
        inherit default description;
      };
    };

  testEither =
    let
      default = "foo";
    in
    {
      expr = parseOption (evalType (lib.types.either lib.types.bool lib.types.str) default);
      expected = {
        oneOf = [
          {
            "$exportedModuleInfo" = {
              path = [ "opt" ];
              default = null;
              defaultText = null;
              required = true;
            };
            type = "boolean";
          }
          {
            "$exportedModuleInfo" = {
              path = [ "opt" ];
              default = null;
              defaultText = null;
              required = true;
            };
            type = "string";
          }
        ];
        inherit default description;
      };
    };

  testAnything =
    let
      default = "foo";
    in
    {
      expr = parseOption (evalType lib.types.anything default);
      expected = {
        inherit default description;
        type = [
          "boolean"
          "integer"
          "number"
          "string"
          "array"
          "object"
          "null"
        ];
      };
    };

  testUnspecified =
    let
      default = "foo";
    in
    {
      expr = parseOption (evalType lib.types.unspecified default);
      expected = {
        inherit default description;
        type = [
          "boolean"
          "integer"
          "number"
          "string"
          "array"
          "object"
          "null"
        ];
      };
    };

  testRaw =
    let
      default = "foo";
    in
    {
      expr = parseOption (evalType lib.types.raw default);
      expected = {
        inherit default description;
        type = [
          "boolean"
          "integer"
          "number"
          "string"
          "array"
          "object"
          "null"
        ];
      };
    };

  test_option_with_default_text = {
    expr = (
      parseOption (evalModuleOptions {
        options.opt = lib.mkOption {
          type = lib.types.bool;
          defaultText = "This option is a optional, but we cannot assign a default value to it yet.";
        };
      })
    );

    expected = {
      additionalProperties = false;
      properties = {
        opt = {
          type = "boolean";
        };
      };
      # opt is not required, because it has a defaultText
      required = [ ];
      type = "object";
    };
  };
  test_nested_option_with_default_text = {
    expr = (
      parseOption (evalModuleOptions {
        options.opt = lib.mkOption {
          type = lib.types.submodule {
            options = {
              foo = lib.mkOption {
                type = lib.types.bool;
                defaultText = "Not required";
              };
            };
          };
          defaultText = "Not required";
        };
      })
    );
    expected = {
      additionalProperties = false;
      properties = {
        opt = {
          additionalProperties = false;
          properties = {
            foo = {
              type = "boolean";
            };
          };
          required = [ ];
          type = "object";
        };
      };
      required = [ ];
      type = "object";
    };
  };
}
