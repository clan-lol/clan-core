{
  lib,
  clanLib,
}:
let
  inherit (lib) types;
  fromModule =
    opts: module:
    let
      jsonschema = clanLib.jsonschema.fromModule (
        {
          typePrefix = "Main";
          addsKeysType = false;
          readOnly = {
            input = false;
            output = false;
          };
          output = false;
        }
        // opts
      ) module;
    in
    jsonschema."$defs";
  fromOption =
    opts: option:
    fromModule opts {
      options.opt = lib.mkOption option;
    };
  fromType =
    opts: type:
    fromOption opts {
      inherit type;
    };
  AnyJson = {
    oneOf = [
      { type = "null"; }
      { type = "boolean"; }
      { type = "integer"; }
      { type = "number"; }
      { type = "string"; }
      {
        type = "array";
        items = {
          "$ref" = "#/$defs/AnyJson";
        };
      }
      {
        type = "object";
        additionalProperties = {
          "$ref" = "#/$defs/AnyJson";
        };
      }
    ];
  };
in
{
  testNested = {
    expr =
      fromModule
        {
          readOnly = {
            input = true;
            output = true;
          };
          output = true;
        }
        {
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
            "$ref" = "#/$defs/MainFooInput";
            readOnly = true;
          };
        };
        additionalProperties = false;
        required = [ "foo" ];
      };
      MainFooInput = {
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
      };
      MainOutput = {
        type = "object";
        properties = {
          foo = {
            "$ref" = "#/$defs/MainFooOutput";
            readOnly = true;
          };
        };
        additionalProperties = false;
        required = [ "foo" ];
      };
      MainFooOutput = {
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
      };
    };
  };
  testNestedOptional = {
    expr = fromModule { readOnly.input = true; } {
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
            "$ref" = "#/$defs/MainFooInput";
            readOnly = true;
          };
        };
        additionalProperties = false;
      };
      MainFooInput = {
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
      };
    };
  };
  testFreeForm = {
    expr = fromModule { readOnly.input = true; } [
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
          type = "object";
          properties = {
            opt = {
              type = "boolean";
              inherit description;
            };
          };
          additionalProperties = false;
          required = [ "opt" ];
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
          text = description;
        };
      };
      expected = {
        MainInput = {
          type = "object";
          properties = {
            opt = {
              type = "boolean";
              inherit description;
            };
          };
          additionalProperties = false;
          required = [ "opt" ];
        };
      };
    };
  testDefaultText = {
    expr = fromOption { } {
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
    expr = fromOption { } {
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
            "$ref" = "#/$defs/MainOptInput";
          };
        };
        additionalProperties = false;
      };
      MainOptInput = {
        type = "object";
        properties = {
          foo = {
            type = "boolean";
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
        type = "object";
        properties = {
          opt = {
            type = "string";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
    };
  };
  testInteger = {
    expr = fromType { } types.int;
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            type = "integer";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
    };
  };
  testFloat = {
    expr = fromType { } types.float;
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            type = "number";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
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
          type = "object";
          properties = {
            opt = {
              "$ref" = "#/$defs/MainOpt";
            };
          };
          additionalProperties = false;
          required = [ "opt" ];
        };
        MainOpt = {
          enum = values;
        };
      };
    };
  testListOfInt = {
    expr = fromType { } (types.listOf types.int);
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            "$ref" = "#/$defs/MainOpt";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];

      };
      MainOpt = {
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
        type = "object";
        properties = {
          opt = {
            "$ref" = "#/$defs/MainOpt";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOpt = {
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
        properties = {
          opt = {
            "$ref" = "#/$defs/MainOpt";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOpt = {
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
        properties = {
          opt = {
            "$ref" = "#/$defs/MainOpt";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOpt = {
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
        properties = {
          opt = {
            "$ref" = "#/$defs/MainOpt";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOpt = {
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
        type = "object";
        properties = {
          opt = {
            oneOf = [
              { type = "null"; }
              { type = "boolean"; }
            ];
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
    };
  };
  testNullOrNullOr = {
    expr = fromType { } (types.nullOr (types.nullOr types.bool));
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            oneOf = [
              { type = "null"; }
              { type = "boolean"; }
            ];
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
    };
  };
  testSubmodule = {
    expr = fromType { } (
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
            "$ref" = "#/$defs/MainOptInput";
          };
        };
        additionalProperties = false;
      };
      MainOptInput = {
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
  };
  testEmptySubmodule = {
    expr = fromType { } (types.submodule { });
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            additionalProperties = false;
            type = "object";
          };
        };
        additionalProperties = false;
      };
    };
  };
  testReadOnlySubmodule = {
    expr = fromModule { readOnly.input = true; } {
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
            "$ref" = "#/$defs/MainFooInput";
            readOnly = true;
          };
        };
        additionalProperties = false;
      };
      MainFooInput = {
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
          opt = {
            "$ref" = "#/$defs/MainOptInput";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOptInput = {
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
    expr =
      fromType { renameType = { loc, name }: if loc == "attrValue" then "MainAttrValue" else name; }
        (
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
        properties = {
          opt = {
            "$ref" = "#/$defs/MainOptInput";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOptInput = {
        type = "object";
        additionalProperties = {
          "$ref" = "#/$defs/MainAttrValueInput";
        };
      };
      MainAttrValueInput = {
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
  testListOfSubmodule = {
    expr =
      fromType { renameType = { loc, name }: if loc == "listItem" then "MainListItem" else name; }
        (
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
        type = "object";
        properties = {
          opt = {
            "$ref" = "#/$defs/MainOptInput";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOptInput = {
        type = "array";
        items = {
          "$ref" = "#/$defs/MainListItemInput";
        };
      };
      MainListItemInput = {
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
  testEither = {
    expr = fromType { } (types.either types.bool types.str);
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            "$ref" = "#/$defs/MainOpt";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOpt = {
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
        type = "object";
        properties = {
          opt = {
            type = "string";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
    };
  };
  testEitherRawOrStr = {
    expr = fromType { } (types.either types.raw types.str);
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            "$ref" = "#/$defs/AnyJson";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      inherit AnyJson;
    };
  };
  testEitherEnum = {
    expr = fromType { } (
      types.either
        (types.enum [
          "a"
          "b"
          "c"
        ])
        (
          types.enum [
            "a"
            "b"
          ]
        )
    );
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            "$ref" = "#/$defs/MainOpt";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOpt = {
        enum = [
          "a"
          "b"
          "c"
        ];
      };
    };
  };
  # testEitherComplexLists = {
  #   expr =
  #     fromType { renameType = { loc, name }: if loc == "listItem" then "MainListItem" else name; }
  #       (
  #         types.either
  #           (types.listOf (
  #             types.enum [
  #               "a"
  #               "b"
  #               "c"
  #             ]
  #           ))
  #           (
  #             types.listOf (
  #               types.enum [
  #                 "a"
  #                 "b"
  #               ]
  #             )
  #           )
  #       );
  #   expected = {
  #     MainInput = {
  #       type = "object";
  #       properties = {
  #         opt = {
  #           "$ref" = "#/$defs/MainOpt";
  #         };
  #       };
  #       additionalProperties = false;
  #       required = [ "opt" ];
  #     };
  #     MainOpt = {
  #       type = "array";
  #       items = {
  #         "$ref" = "#/$defs/MainListItem";
  #       };
  #     };
  #     MainListItem = {
  #       enum = [
  #         "a"
  #         "b"
  #         "c"
  #       ];
  #     };
  #   };
  # };
  testCoercedTo = {
    expr = fromType { output = true; } (types.coercedTo types.int toString types.str);
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            "$ref" = "#/$defs/MainOptInput";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOptInput = {
        oneOf = [
          { type = "integer"; }
          { type = "string"; }
        ];
      };
      MainOutput = {
        type = "object";
        properties = {
          opt = {
            # Should not use $ref here, because it's a simple type
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
          renameType =
            { loc, name }:
            if loc == "listOf" then
              "MainList"
            else if loc == "attrsOf" then
              "MainAttrs"
            else
              name;
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
            "$ref" = "#/$defs/MainOptInput";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOptInput = {
        oneOf = [
          { "$ref" = "#/$defs/MainList"; }
          { "$ref" = "#/$defs/MainAttrs"; }
        ];
      };
      MainList = {
        type = "array";
        items = {
          type = "string";
        };
      };
      MainAttrs = {
        type = "object";
        additionalProperties = {
          type = "string";
        };
      };
      MainOutput = {
        type = "object";
        properties = {
          opt = {
            "$ref" = "#/$defs/MainAttrs";
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
        type = "object";
        properties = {
          opt = {
            "$ref" = "#/$defs/AnyJson";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      inherit AnyJson;
    };
  };
  testComplexCoerced = {
    expr =
      fromType
        {
          renameType =
            { loc, name }:
            if loc == "listOf" then
              "MainList"
            else if loc == "attrsOf" then
              "MainAttrs"
            else
              name;
        }
        (
          types.coercedTo (types.listOf types.str) (t: lib.genAttrs t (_: { })) (
            types.attrsOf (types.submodule { })
          )
        );
    expected = {
      MainInput = {
        type = "object";
        properties = {
          opt = {
            "$ref" = "#/$defs/MainOptInput";
          };
        };
        additionalProperties = false;
        required = [ "opt" ];
      };
      MainOptInput = {
        oneOf = [
          { "$ref" = "#/$defs/MainList"; }
          { "$ref" = "#/$defs/MainAttrs"; }
        ];
      };
      MainList = {
        type = "array";
        items = {
          type = "string";
        };
      };
      MainAttrs = {
        type = "object";
        additionalProperties = {
          type = "object";
          additionalProperties = false;
        };
      };
    };
  };
  testFlatten =
    let
      flattenOneOf = import ./flattenOneOf.nix { inherit lib clanLib; };
    in
    {
      expr = flattenOneOf { } [
        {
          type = "array";
          items = {
            type = "string";
          };
        }
        {
          type = "object";
          additionalProperties = {
            type = "object";
            additionalProperties = false;
          };
        }
      ];
      expected = {
        defs = { };
        oneOf = [
          {
            type = "array";
            items = {
              type = "string";
            };
          }
          {
            type = "object";
            additionalProperties = {
              type = "object";
              additionalProperties = false;
            };
          }
        ];
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
              type = "object";
              properties = {
                opt = {
                  "$ref" = "#/$defs/AnyJson";
                };
              };
              additionalProperties = false;
              required = [ "opt" ];
            };
            inherit AnyJson;
          };
        }
      );
  testRenameAttrType = {
    expr = fromType {
      addsTitle = true;
      renameType = { loc, name }: if loc == "attrValue" then "OptModule" else name;
    } (types.attrsOf types.deferredModule);
    expected = {
      inherit AnyJson;
      MainInput = {
        additionalProperties = false;
        properties = {
          opt = {
            "$ref" = "#/$defs/MainOpt";
          };
        };
        required = [ "opt" ];
        type = "object";
      };
      MainOpt = {
        additionalProperties = {
          "$ref" = "#/$defs/AnyJson";
        };
        type = "object";
      };
    };
    # MainInput = {
    #   title = "MainOpt";
    #   type = "object";
    #   additionalProperties = {
    #     title = "OptModule";
    #     type = "object";
    #     additionalProperties = {
    #       "$ref" = "#/$defs/AnyJson";
    #     };
    #   };
    # };
    # inherit AnyJson;
    # };
  };
}
