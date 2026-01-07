{
  lib ? import <nixpkgs/lib>,
  clanLib,
}:
let
  # ============================================================================
  # Constants
  # ============================================================================

  # To facilitate the flattening of branches in options like either, we give
  # $ref an inlined structure where it contains both the type name and the
  # referenced jsonschema.
  #
  # This is not valid jsonschema, So at the entrypoint, we travel the
  # jsonschema tree and convert it back to a valid one.
  ref = typeName: jsonschema: {
    "$ref" = {
      inherit typeName jsonschema;
    };
  };
  AnyJson = {
    "$ref" = {
      typeName = "AnyJson";
      jsonschema = {
        oneOf = [
          { type = "null"; }
          { type = "boolean"; }
          { type = "integer"; }
          { type = "number"; }
          { type = "string"; }
          {
            type = "array";
            items = AnyJson;
          }
          {
            type = "object";
            additionalProperties = AnyJson;
          }
        ];
      };
    };
  };

  # ============================================================================
  # Option Checkers
  # ============================================================================
  #
  isIncludedOption = option: option.visible or true;
  #
  toBroaderOptionType =
    option:
    {
      bool = "boolean";
      boolByOr = "boolean";

      # TODO: Add support for intMatching in jsonschema
      int = "integer";
      intBetween = "integer";
      positiveInt = "integer";
      unsignedInt = "integer";
      unsignedInt8 = "integer";
      # This also includes port
      unsignedInt16 = "integer";
      unsignedInt32 = "integer";
      signedInt8 = "integer";
      signedInt16 = "integer";
      signedInt32 = "integer";

      float = "number";
      numberBetween = "number";
      numberNonnegative = "number";
      numberPositive = "number";

      str = "string";
      nonEmptyStr = "string";
      singleLineStr = "string";
      separatedString = "string";
      path = "string";

      enum = "enum";
      nullOr = "nullOr";
      either = "either";
      coercedTo = "coercedTo";
      attrs = "attrs";
      submodule = "submodule";
      listOf = "listOf";
      attrsOf = "attrsOf";
      lazyAttrsOf = "attrsOf";

      anything = "any";
      unspecified = "any";
      raw = "any";
      # This is a special case for the deferred clan.service 'settings', we
      # assume it is JSON serializable To get the type of a Deferred modules we
      # need to know the interface of the place where it is evaluated. i.e. in
      # case of a clan.service this is the interface of the service which
      # dynamically changes depending on the service
      #
      # We can assign the type later, when we know the exact interface.
      deferredModule = "any";
    }
    .${option.type.name} or (
      if lib.strings.hasPrefix "strMatching " option.type.name then
        "string"
      else if lib.strings.hasPrefix "passwdEntry " option.type.name then
        "string"
      else
        lib.trace option throw ''
          option type '${option.type.name}' ('${option.type.description}') not supported by jsonschema converter
          location: ${lib.showOption option.loc}
        ''
    );

  # ============================================================================
  # Main Conversion Functions
  # ============================================================================

  /**
    Takes a nix option and returns a node (or null) with this structure:

    ```nix
    {
      # jsonschema this option generates. Notice this might not strictly be
      # valid jsonschema when it contains $ref. To help facilitate flattening
      # branches in types like either. See the ref function on the custom
      # $ref structure
      jsonschema = {
        type = "boolean";
      }

      # If this option has a default value. It's used to decide when contained
      # in something that generates to an jsonschema object, its `required`
      # should contain the propery name that corresponds to this option.
      isRequired = true | false
    }
    ```
  */
  optionToNode =
    ctx@{
      typePrefix,
      mode,
      # Inside a branch of `eitehr` or input mode of `coercedTo`, types like
      # enum or one of shouldn't create a new type, because they might be merged
      # with other branches. only the outside type should create a new type.
      # But inside an attrs which is inside a branch, a custom type should be
      # created again;
      shouldInlineBranchTypes ? false,
      renamedTypes,
      ...
    }:
    option:
    let
      isRequired = mode == "output" || !(option ? default) && !(option ? defaultText);
      description = lib.optionalAttrs (option ? description) {
        description = option.description.text or option.description;
      };
      getRenamedType = name: renamedTypes.${name} or name;
      /**
        When a branch option like either eventually flattens to a single branch,
        check if it should have its own type name based on the jsonschema type
      */
      shouldDefineBranchType =
        jsonschema:
        !shouldInlineBranchTypes
        && (
          (
            jsonschema ? type
            && lib.elem jsonschema.type [
              "array"
              "object"
            ]
          )
          || jsonschema ? enum
          || jsonschema ? oneOf
        );
      subctx = ctx // {
        inherit
          isRequired
          description
          getRenamedType
          shouldInlineBranchTypes
          shouldDefineBranchType
          ;
      };
      broaderOptionType = toBroaderOptionType option;
      simpleNode = {
        jsonschema = {
          type = broaderOptionType;
        }
        // description;
        inherit isRequired;
      };
    in
    if !isIncludedOption option then
      null
    else
      {
        boolean = simpleNode;
        integer = simpleNode;
        number = simpleNode;
        string = simpleNode;
        enum = mkEnumNode subctx option;
        nullOr = mkNullOrNode subctx option;
        either = mkEitherNode subctx option;
        coercedTo = mkCoercedToNode subctx option;
        attrs = mkAttrsNode subctx option;
        submodule = mkSubmoduleNode subctx option;
        listOf = mkListOfNode subctx option;
        attrsOf = mkAttrsOfNode subctx option;
        any = {
          jsonschema = AnyJson // description;
          inherit isRequired;
        };
      }
      .${broaderOptionType} or (throw "Unhandled broaderOptionType");

  /**
    Refer to `optionToNode`'s doc for the definition of a node
  */
  attrsOfOptionsToNode =
    ctx@{
      typePrefix,
      mode,
      renamedTypes,
      submoduleInfo ? null,
      ...
    }:
    attrsOfOptions:
    let
      getRenamedType = name: renamedTypes.${name} or name;

      relevantOptions = removeAttrs attrsOfOptions [
        "_module"
        "_freeformOptions"
      ];

      /**
        Map every option to a node
        Some options mapped to null get filtered out. i.e. those that are not "visible"
      */
      nodesAttrs = lib.filterAttrs (_: v: v != null) (
        lib.mapAttrs (
          name: attrsOrOption:
          let
            subctx = ctx // {
              # We need to use toUpperFirst here because name might be "extraModules"
              # and we want to turn it into "ExtraModules", toSentenceCase turns it
              # to "Extramodules" which is not what we want
              typePrefix = getRenamedType (ctx.typePrefix + clanLib.toUpperFirst name);
              shouldInlineBranchTypes = false;
            };
          in
          if lib.isOption attrsOrOption then
            optionToNode subctx attrsOrOption
          else
            attrsOfOptionsToNode subctx attrsOrOption
        ) relevantOptions
      );

      freeformNode =
        let
          # freeformType will have more than 1 definitions if it's specified in
          # multiple modules. In that case we assume they are all the same, and
          # we just take the first one. We also assume it's always attsOf
          # something. If those are not the case, we silently ignore
          # freeformType. definitions are never empty, because freeformType has
          # a default value of null
          freeformOption = attrsOfOptions._module.freeformType or null;
          nestedType =
            if freeformOption == null then
              null
            else
              (lib.head freeformOption.definitions).nestedTypes.elemType or null;
          nestedOption = {
            type = nestedType;
            _type = "option";
            loc = freeformOption.loc;
          };
        in
        if nestedType == null then
          null
        else
          optionToNode (
            ctx
            // {
              typePrefix = getRenamedType (typePrefix + "Freeform");
            }
          ) nestedOption;
      properties = lib.mapAttrs (
        _name: node:
        node.jsonschema
        //
          # Setting readOnly llows assigning an output
          # type to the corresponding input type. Currently it will complain that a
          # required property can not be passed to a non-required one.
          # We do this in the unit tests:
          #   machine_jon = get_machine(flake, "jon")
          #   set_machine(Machine("jon", flake), machine_jon)
          lib.optionalAttrs (ctx.readOnly.${mode} or true) {
            readOnly = true;
          }
      ) nodesAttrs;

      required = lib.attrNames (lib.filterAttrs (_name: node: node.isRequired) nodesAttrs);
      typeName = getRenamedType typePrefix + lib.toSentenceCase mode;
      jsonschema = {
        type = "object";
        additionalProperties = if freeformNode == null then false else freeformNode.jsonschema;
        # Make sure to not add readOnly here
        # a property should only have readOnly if it's a direct child of an
        # object, by itself it doesn't know if that's the case;
      }
      // lib.optionalAttrs (submoduleInfo.description or null != null) {
        description = submoduleInfo.description;
      }
      // lib.optionalAttrs (properties != { }) {
        inherit properties;
      }
      // lib.optionalAttrs (required != [ ]) {
        inherit required;
      };
    in
    {
      jsonschema = ref typeName jsonschema;
      # This property is `required` if none of its child properties has a
      # default value (i.e., some of its child property's isRequired is true)
      isRequired = if submoduleInfo == null then required != [ ] else submoduleInfo.isRequired;
    };

  mkEnumNode =
    ctx@{
      mode,
      typePrefix,
      isRequired,
      description,
      getRenamedType,
      ...
    }:
    option:
    let
      typeName = getRenamedType (typePrefix + lib.toSentenceCase mode);
      jsonschema = {
        enum = option.type.functor.payload.values;
      }
      // description;
    in
    {
      jsonschema = ref typeName jsonschema;
      inherit isRequired;
    };

  mkNullOrNode =
    ctx@{
      mode,
      isRequired,
      description,
      ...
    }:
    option:
    let
      nestedOption = {
        type = option.type.nestedTypes.elemType;
        _type = "option";
        loc = option.loc;
      };
      node = optionToNode ctx nestedOption;
      oneOf = flattenOneOf ([ { type = "null"; } ] ++ (lib.optional (node != null) node.jsonschema));
      jsonschema = (if lib.length oneOf == 1 then lib.head oneOf else { inherit oneOf; }) // description;
    in
    {
      inherit jsonschema isRequired;
    };

  mkEitherNode =
    ctx@{
      mode,
      typePrefix,
      description,
      isRequired,
      shouldDefineBranchType,
      getRenamedType,
      ...
    }:
    option:
    let
      nodesAttrs =
        lib.mapAttrs
          (
            name: type:
            let
              subctx = ctx // {
                typePrefix = getRenamedType (
                  typePrefix + lib.optionalString (numOneOf >= 2) (lib.toSentenceCase name)
                );
                shouldInlineBranchTypes = true;
              };
            in
            optionToNode subctx {
              inherit type;
              _type = "option";
              loc = option.loc;
            }
          )
          {
            left = option.type.nestedTypes.left;
            right = option.type.nestedTypes.right;
          };
      nodes = lib.concatAttrValues (
        lib.mapAttrs (_name: node: if node == null then [ ] else [ node ]) nodesAttrs
      );
      oneOf = flattenOneOf (map (node: node.jsonschema) nodes);
      numOneOf = lib.length oneOf;
      typeName = getRenamedType typePrefix + lib.toSentenceCase mode;
      jsonschema = (if numOneOf == 1 then lib.head oneOf else { inherit oneOf; }) // description;
    in
    if nodesAttrs.left == null && nodesAttrs.right == null then
      null
    else
      {
        jsonschema = if shouldDefineBranchType jsonschema then ref typeName jsonschema else jsonschema;
        inherit isRequired;
      };

  mkCoercedToNode =
    ctx@{
      mode,
      typePrefix,
      description,
      isRequired,
      getRenamedType,
      shouldDefineBranchType,
      ...
    }:
    option:
    let
      nodesAttrs =
        lib.mapAttrs
          (
            name: type:
            let
              subctx = ctx // {
                typePrefix = getRenamedType (
                  typePrefix + lib.optionalString (numOneOf >= 2) (lib.toSentenceCase name)
                );
                shouldInlineBranchTypes = mode == "input";
              };
            in
            optionToNode subctx {
              inherit type;
              _type = "option";
              loc = option.loc;
            }
          )
          {
            from = option.type.nestedTypes.coercedType;
            to = option.type.nestedTypes.finalType;
          };
      nodes = lib.concatAttrValues (
        lib.mapAttrs (_name: node: if node == null then [ ] else [ node ]) nodesAttrs
      );
      oneOf =
        if mode == "input" then
          flattenOneOf (map (node: node.jsonschema) nodes)
        else
          [ nodesAttrs.to.jsonschema ];
      numOneOf = lib.length oneOf;
      jsonschema = (if numOneOf == 1 then lib.head oneOf else { inherit oneOf; }) // description;
      typeName = getRenamedType typePrefix + lib.toSentenceCase mode;
    in
    # If this option can result in null for either input or output, neither
    # input or output should include this type
    if nodesAttrs.from == null || nodesAttrs.to == null then
      null
    else
      {
        jsonschema =
          if mode == "input" && shouldDefineBranchType jsonschema then
            ref typeName jsonschema
          else
            jsonschema;
        inherit isRequired;
      };

  mkAttrsNode =
    ctx@{
      mode,
      typePrefix,
      description,
      isRequired,
      getRenamedType,
      ...
    }:
    option:
    let
      typeName = getRenamedType typePrefix + lib.toSentenceCase mode;
      jsonschema = {
        type = "object";
        additionalProperties = AnyJson;
      }
      // description;
    in
    {
      jsonschema = ref typeName jsonschema;
      inherit isRequired;
    };

  mkSubmoduleNode =
    ctx@{
      isRequired,
      description,
      ...
    }:
    option:
    let
      subOptions = option.type.getSubOptions option.loc;
      node = attrsOfOptionsToNode (
        ctx
        // {
          submoduleInfo = {
            inherit isRequired;
          }
          // description;
        }
      ) subOptions;
    in
    node;

  mkListOfNode =
    ctx@{
      mode,
      typePrefix,
      isRequired,
      description,
      getRenamedType,
      ...
    }:
    option:
    let
      nestedOption = {
        type = option.type.nestedTypes.elemType;
        _type = "option";
        loc = option.loc;
      };
      node = optionToNode (
        ctx
        // {
          typePrefix = getRenamedType (typePrefix + "Item");
          shouldInlineBranchTypes = false;
        }
      ) nestedOption;
      typeName = getRenamedType typePrefix + lib.toSentenceCase mode;
      jsonschema = {
        type = "array";
        items = node.jsonschema;
      }
      // description;
    in
    if node == null then
      null
    else
      {
        jsonschema = ref typeName jsonschema;
        inherit isRequired;
      };

  mkAttrsOfNode =
    ctx@{
      mode,
      typePrefix,
      isRequired,
      description,
      getRenamedType,
      ...
    }:
    option:
    let
      nestedOption = {
        type = option.type.nestedTypes.elemType;
        _type = "option";
        loc = option.loc;
      };
      node = optionToNode (
        ctx
        // {
          typePrefix = getRenamedType (typePrefix + "Item");
          shouldInlineBranchTypes = false;
        }
      ) nestedOption;
      typeName = getRenamedType typePrefix + lib.toSentenceCase mode;
      jsonschema = {
        type = "object";
        additionalProperties = node.jsonschema;
      }
      // description;
    in
    if node == null then
      null
    else
      {
        jsonschema = ref typeName jsonschema;
        inherit isRequired;
      };

  # ============================================================================
  # Jsonschema Handlers
  # ============================================================================

  flattenOneOf = import ./flattenOneOf.nix {
    inherit lib clanLib;
  };

  resolveRefs =
    resolvedNames: jsonschema:
    if jsonschema ? "$ref" then
      let
        inherit (jsonschema."$ref") typeName;
        result = resolveRefs (resolvedNames // { ${typeName} = true; }) jsonschema."$ref".jsonschema;
      in
      {
        jsonschema = jsonschema // {
          "$ref" = "#/$defs/${typeName}";
        };
        defs =
          if resolvedNames ? ${typeName} then
            { }
          else
            result.defs
            // {
              ${typeName} = result.jsonschema;
            };
      }
    else if jsonschema ? oneOf then
      let
        results = map (branch: resolveRefs resolvedNames branch) jsonschema.oneOf;
      in
      {
        jsonschema = jsonschema // {
          oneOf = map (result: result.jsonschema) results;
        };
        defs = clanLib.concatMapListToAttrs (result: result.defs) results;
      }
    else if jsonschema.type or null == "array" then
      let
        itemsResult = lib.optionalAttrs (jsonschema ? items) (resolveRefs resolvedNames jsonschema.items);
      in
      {
        jsonschema =
          jsonschema
          // lib.optionalAttrs (itemsResult != { }) {
            items = itemsResult.jsonschema;
          };
        defs = itemsResult.defs or { };
      }
    else if jsonschema.type or null == "object" then
      let
        propsResults = lib.mapAttrs (
          _name: jsonschema: resolveRefs resolvedNames jsonschema
        ) jsonschema.properties or { };
        additPropsResult = lib.optionalAttrs (jsonschema ? additionalProperties) (
          resolveRefs resolvedNames jsonschema.additionalProperties
        );
      in
      {
        jsonschema =
          jsonschema
          // lib.optionalAttrs (propsResults != { }) {
            properties = lib.mapAttrs (_name: result: result.jsonschema) propsResults;
          }
          // lib.optionalAttrs (additPropsResult != { }) {
            additionalProperties = additPropsResult.jsonschema;
          };
        # Letting defs in properties override those in additionalProperties is
        # intentional. In the case of a submodule with freeform, and freeform
        # results in the same jsonschema type as a proeprty, we want the
        # property's jsonschema to override freenode's jsonschema, because the
        # latter is less likely to contain a description
        defs = additPropsResult.defs or { } // lib.concatMapAttrs (_name: result: result.defs) propsResults;
      }
    else
      {
        inherit jsonschema;
        defs = { };
      };
in
rec {
  fromOptions =
    {
      typePrefix,
      input ? true,
      output ? true,
      readOnly ? {
        input = true;
        output = true;
      },
      renamedTypes ? { },
    }:
    options:
    let
      inputNode = attrsOfOptionsToNode {
        mode = "input";
        inherit
          typePrefix
          readOnly
          renamedTypes
          ;
      } options;
      inputResult = resolveRefs { } inputNode.jsonschema;
      outputNode = attrsOfOptionsToNode {
        mode = "output";
        inherit
          typePrefix
          readOnly
          renamedTypes
          ;
      } options;
      outputResult = resolveRefs { } outputNode.jsonschema;
    in
    assert lib.assertMsg (input || output) "either input or output must be true";
    assert lib.assertMsg (
      input -> inputNode != null
    ) "options must not result in an empty schema for input";
    assert lib.assertMsg (
      output -> outputNode != null
    ) "options must not result in an empty schema for output";
    {
      "$schema" = "https://json-schema.org/draft/2020-12/schema";
      "$defs" = lib.optionalAttrs input inputResult.defs // lib.optionalAttrs output outputResult.defs;
    };
  fromModule =
    opts: module:
    let
      evaled = lib.evalModules {
        modules = lib.toList module;
      };
      jsonschema = fromOptions opts evaled.options;
    in
    jsonschema;
}
