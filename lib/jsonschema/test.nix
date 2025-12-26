{
  lib,
  clanLib,
}:
let
  inherit (lib) types;
  fromModule =
    opts@{
      typePrefix ? "Main",
      addsTitle ? false,
      addsKeysType ? false,
      ...
    }:
    module:
    let
      opts' = opts // {
        inherit typePrefix addsTitle addsKeysType;
      };
      jsonschema = clanLib.jsonschema.fromModule opts' module;
    in
    jsonschema."$defs";
  fromOption =
    opts@{
      input ? true,
      output ? false,
      clipToOption ? true,
      optionName ? "opt",
      typePrefix ? "Main",
      readOnly ? {
        input = false;
        output = false;
      },
      ...
    }:
    option:
    let
      opts' =
        lib.removeAttrs opts [
          "optionName"
          "clipToOption"
        ]
        // {
          inherit
            input
            output
            typePrefix
            readOnly
            ;
        };
      result = fromModule opts' {
        options.${optionName} = lib.mkOption option;
      };
    in
    result
    // lib.optionalAttrs clipToOption (
      lib.optionalAttrs input {
        "${typePrefix}Input" = result."${typePrefix}Input".properties.${optionName};
      }
      // lib.optionalAttrs output {
        "${typePrefix}Output" = result."${typePrefix}Output".properties.${optionName};
      }
    );
  fromType =
    opts: type:
    fromOption opts {
      inherit type;
    };
  AnyJson = {
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
in
{
  testNested = {
    expr = fromModule { } {
      options.foo.bar = lib.mkOption {
        type = types.bool;
      };
      options.foo.baz = lib.mkOption {
        type = types.bool;
        default = false;
      };
    };
    expected = {
      MainInput = {
        type = "object";
        properties = {
          foo = {
            additionalProperties = false;
            properties = {
              bar = {
                type = "boolean";
                readOnly = true;
              };
              baz = {
                type = "boolean";
                readOnly = true;
              };
            };
            type = "object";
            required = [ "bar" ];
            readOnly = true;
          };
        };
        additionalProperties = false;
        required = [ "foo" ];
      };
      MainOutput = {
        type = "object";
        properties = {
          foo = {
            additionalProperties = false;
            properties = {
              bar = {
                type = "boolean";
                readOnly = true;
              };
              baz = {
                type = "boolean";
                readOnly = true;
              };
            };
            type = "object";
            required = [
              "bar"
              "baz"
            ];
            readOnly = true;
          };
        };
        additionalProperties = false;
        required = [ "foo" ];
      };
    };
  };
  testNestedOptional = {
    expr = fromModule { output = false; } {
      options.foo.bar = lib.mkOption {
        type = types.str;
        default = "bar";
      };
      options.foo.baz = lib.mkOption {
        type = types.port;
        default = 22;
      };
    };
    expected = {
      MainInput = {
        type = "object";
        properties = {
          foo = {
            type = "object";
            properties = {
              bar = {
                type = "string";
                readOnly = true;
              };
              baz = {
                type = "integer";
                readOnly = true;
              };
            };
            additionalProperties = false;
            readOnly = true;
          };
        };
        additionalProperties = false;
      };
    };
  };
  testFreeForm = {
    expr = fromModule { output = false; } [
      {
        freeformType = types.attrsOf types.int;
        options = {
          enable = lib.mkEnableOption "enable this";
        };
      }
      {
        foo = 1;
        bar = 2;
      }
    ];
    expected = {
      MainInput = {
        type = "object";
        properties = {
          enable = {
            type = "boolean";
            description = "Whether to enable enable this.";
            readOnly = true;
          };
        };
        additionalProperties = {
          type = "integer";
        };
      };
    };
  };
  testDescription =
    let
      description = "foo";
    in
    {
      expr = fromOption { } {
        type = types.bool;
        inherit description;
      };
      expected = {
        MainInput = {
          type = "boolean";
          inherit description;
        };
      };
    };
  testAttrsDescription =
    let
      description = "foo";
    in
    {
      expr = fromOption { } {
        type = types.bool;
        description = {
          _type = "mdDoc";
          text = "foo";
        };
      };
      expected = {
        MainInput = {
          type = "boolean";
          inherit description;
        };
      };
    };
  testDefaultText = {
    expr =
      fromOption
        {
          clipToOption = false;
        }
        {
          type = types.bool;
          defaultText = "Not required";
        };
    expected = {
      MainInput = {
        type = "object";
        # opt is not required, because it has a defaultText
        properties = {
          opt = {
            type = "boolean";
          };
        };
        additionalProperties = false;
      };
    };
  };
  testNestedDefaultText = {
    expr =
      fromOption
        {
          clipToOption = false;
        }
        {
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
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            type = "object";
            properties = {
              foo = {
                type = "boolean";
              };
            };
            additionalProperties = false;
          };
        };
        additionalProperties = false;
      };
    };
  };
  testString = {
    expr = fromType { } types.str;
    expected = {
      MainInput = {
        type = "string";
      };
    };
  };
  testInteger = {
    expr = fromType { } types.int;
    expected = {
      MainInput = {
        type = "integer";
      };
    };
  };
  testFloat = {
    expr = fromType { } types.float;
    expected = {
      MainInput = {
        type = "number";
      };
    };
  };
  testEnum =
    let
      values = [
        "foo"
        "bar"
        "baz"
      ];
    in
    {
      expr = fromType { } (types.enum values);
      expected = {
        MainInput = {
          enum = values;
        };
      };
    };
  testListOfInt = {
    expr = fromType { } (types.listOf types.int);
    expected = {
      MainInput = {
        type = "array";
        items = {
          type = "integer";
        };
      };
    };
  };
  testListOfUnspecified = {
    expr = fromType { } (types.listOf types.unspecified);
    expected = {
      MainInput = {
        type = "array";
        items = {
          "$ref" = "#/$defs/AnyJson";
        };
      };
      inherit AnyJson;
    };
  };
  testAttrs = {
    expr = fromType { } types.attrs;
    expected = {
      MainInput = {
        type = "object";
        additionalProperties = {
          "$ref" = "#/$defs/AnyJson";
        };
      };
      inherit AnyJson;
    };
  };
  testAttrsOfInt = {
    expr = fromType { } (types.attrsOf types.int);
    expected = {
      MainInput = {
        type = "object";
        additionalProperties = {
          type = "integer";
        };
      };
    };
  };
  testLazyAttrsOfInt = {
    expr = fromType { } (types.lazyAttrsOf types.int);
    expected = {
      MainInput = {
        type = "object";
        additionalProperties = {
          type = "integer";
        };
      };
    };
  };
  testNullOrBool = {
    expr = fromType { } (types.nullOr types.bool);
    expected = {
      MainInput = {
        oneOf = [
          { type = "null"; }
          { type = "boolean"; }
        ];
      };
    };
  };
  testNullOrNullOr = {
    expr = fromType { } (types.nullOr (types.nullOr types.bool));
    expected = {
      MainInput = {
        oneOf = [
          { type = "null"; }
          { type = "boolean"; }
        ];
      };
    };
  };
  testSubmodule = {
    expr = fromType { clipToOption = false; } (
      types.submodule {
        options.bar = lib.mkOption {
          type = types.int;
          default = 0;
        };
        options.baz = lib.mkOption {
          type = types.float;
          default = 1.1;
        };
      }
    );
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            type = "object";
            properties = {
              bar = {
                type = "integer";
              };
              baz = {
                type = "number";
              };
            };
            additionalProperties = false;
          };
        };
        additionalProperties = false;
      };
    };
  };
  testReadOnlySubmodule = {
    expr =
      fromModule
        {
          output = false;
          readOnly = {
            input = true;
          };
        }
        {
          options.foo = lib.mkOption {
            type = types.submodule {
              options.bar = lib.mkOption {
                type = types.int;
                default = 0;
              };
              options.baz = lib.mkOption {
                type = types.float;
                default = 1.1;
              };
            };
          };
        };
    expected = {
      MainInput = {
        type = "object";
        properties = {
          foo = {
            type = "object";
            properties = {
              bar = {
                type = "integer";
                readOnly = true;
              };
              baz = {
                type = "number";
                readOnly = true;
              };
            };
            additionalProperties = false;
            readOnly = true;
          };
        };
        additionalProperties = false;
      };
    };
  };
  testSubmoduleWithoutDefault = {
    expr = fromType { } (
      types.submodule {
        options.bar = lib.mkOption {
          type = types.int;
        };
      }
    );
    expected = {
      MainInput = {
        type = "object";
        properties = {
          bar = {
            type = "integer";
          };
        };
        additionalProperties = false;
        required = [ "bar" ];
      };
    };
  };
  testAttrsOfSubmodule = {
    expr = fromType { } (
      types.attrsOf (
        types.submodule {
          options.bar = lib.mkOption {
            type = types.bool;
          };
        }
      )
    );
    expected = {
      MainInput = {
        type = "object";
        additionalProperties = {
          type = "object";
          properties = {
            bar = {
              type = "boolean";
            };
          };
          additionalProperties = false;
          required = [ "bar" ];
        };
      };
    };
  };
  testListOfSubmodule = {
    expr = fromType { } (
      types.listOf (
        types.submodule {
          options.bar = lib.mkOption {
            type = types.bool;
          };
        }
      )
    );
    expected = {
      MainInput = {
        type = "array";
        items = {
          type = "object";
          properties = {
            bar = {
              type = "boolean";
            };
          };
          additionalProperties = false;
          required = [ "bar" ];
        };
      };
    };
  };
  testEither = {
    expr = fromType { } (types.either types.bool types.str);
    expected = {
      MainInput = {
        oneOf = [
          { type = "boolean"; }
          { type = "string"; }
        ];
      };
    };
  };
  testEitherFunctionTo = {
    expr = fromType { } (types.either (types.functionTo types.str) types.str);
    expected = {
      MainInput = {
        type = "string";
      };
    };
  };
  testEitherRawOrStr = {
    expr = fromType { } (types.either types.raw types.str);
    expected = {
      MainInput = {
        "$ref" = "#/$defs/AnyJson";
      };
      inherit AnyJson;
    };
  };
  testEitherComplexLists = {
    expr = fromType { } (
      types.either
        (types.listOf (
          types.enum [
            "a"
            "b"
            "c"
          ]
        ))
        (
          types.listOf (
            types.enum [
              "a"
              "b"
            ]
          )
        )
    );
    expected = {
      MainInput = {
        type = "array";
        items = {
          enum = [
            "a"
            "b"
            "c"
          ];
        };
      };
    };
  };
  testCoercedTo = {
    expr = fromType {
      output = true;
      clipToOption = false;
      addsTitle = true;
    } (types.coercedTo types.int toString types.str);
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            title = "MainOptInput";
            oneOf = [
              { type = "integer"; }
              { type = "string"; }
            ];
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOutput = {
        type = "object";
        properties = {
          opt = {
            # Should not add title here, because it's a simple type
            type = "string";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
    };
  };
  testCoercedToAttrs = {
    expr =
      fromType
        {
          output = true;
          clipToOption = false;
          addsTitle = true;
        }
        (
          types.coercedTo (types.listOf types.str) (
            strs:
            lib.genAttrs strs (s: {
              ${s} = s;
            })
          ) (types.attrsOf types.str)
        );
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            title = "MainOptInput";
            oneOf = [
              {
                # This colliding name is expected, since we don't renameType
                title = "MainOptInput";
                type = "array";
                items = {
                  type = "string";
                };
              }
              {
                # This colliding name is expected, since we don't renameType
                title = "MainOptInput";
                type = "object";
                additionalProperties = {
                  type = "string";
                };
              }
            ];
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOutput = {
        type = "object";
        properties = {
          opt = {
            title = "MainOptOutput";
            type = "object";
            additionalProperties = {
              type = "string";
            };
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
    };
  };
  testCoercedRawToPath = {
    expr = fromType { } (types.coercedTo types.raw lib.id types.path);
    expected = {
      MainInput = {
        "$ref" = "#/$defs/AnyJson";
      };
      inherit AnyJson;
    };
  };
  AnyJson =
    lib.genAttrs'
      [
        "anything"
        "unspecified"
        "raw"
      ]
      (
        name:
        lib.nameValuePair "test${lib.toSentenceCase name}" {
          expr = fromType { } types.${name};
          expected = {
            MainInput = {
              "$ref" = "#/$defs/AnyJson";
            };
            inherit AnyJson;
          };
        }
      );
  testRenameAttrType = {
    expr = fromType {
      addsTitle = true;
      renameType = { loc, name }: if loc == "attrsOfItem" then "OptModule" else name;
    } (types.attrsOf types.deferredModule);
    expected = {
      MainInput = {
        title = "MainOpt";
        type = "object";
        additionalProperties = {
          title = "OptModule";
          type = "object";
          additionalProperties = {
            "$ref" = "#/$defs/AnyJson";
          };
        };
      };
      inherit AnyJson;
    };
  };
}
