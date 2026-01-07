{
  lib ? import <nixpkgs/lib>,
  clanLib,
}:
let
  # ============================================================================
  # Constants and Basic Helpers
  # ============================================================================

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

  flattenOneOf = import ./flattenOneOf.nix {
    inherit lib clanLib;
  };

  # ============================================================================
  # Type Checkers
  # ============================================================================
  #
  isIncludedOption = option: option.visible or true;
  #
  isBoolOption =
    option:
    {
      bool = true;
      boolByOr = true;
    }
    .${option.type.name} or false;
  #
  isIntOption =
    option:
    {
      # TODO: Add support for intMatching in jsonschema
      int = true;
      intBetween = true;
      positiveInt = true;
      unsignedInt = true;
      unsignedInt8 = true;
      # This also includes port
      unsignedInt16 = true;
      unsignedInt32 = true;
      signedInt8 = true;
      signedInt16 = true;
      signedInt32 = true;
    }
    .${option.type.name} or false;
  #
  isFloatOption =
    option:
    {
      float = true;
      numberBetween = true;
      numberNonnegative = true;
      numberPositive = true;
    }
    .${option.type.name} or false;
  #
  isStrOption =
    option:
    {
      str = true;
      nonEmptyStr = true;
      singleLineStr = true;
      separatedString = true;
      path = true;
    }
    .${option.type.name} or (
      if lib.strings.hasPrefix "strMatching " option.type.name then
        true
      else if lib.strings.hasPrefix "passwdEntry " option.type.name then
        true
      else
        false
    );
  #
  isAnyOption =
    option:
    {
      anything = true;
      unspecified = true;
      raw = true;
      # This is a special case for the deferred clan.service 'settings', we
      # assume it is JSON serializable To get the type of a Deferred modules we
      # need to know the interface of the place where it is evaluated. i.e. in
      # case of a clan.service this is the interface of the service which
      # dynamically changes depending on the service
      #
      # We can assign the type later, when we know the exact interface.
      deferredModule = true;
    }
    .${option.type.name} or false;

  # ============================================================================
  # Type Handlers
  # ============================================================================

  mkSimpleNode = type: description: isRequired: {
    jsonschema = {
      inherit type;
    }
    // description;
    inherit isRequired;
  };

  # Trivial nodes
  handleBool = ctx: mkSimpleNode "boolean" ctx.description ctx.isRequired;
  handleInt = ctx: mkSimpleNode "integer" ctx.description ctx.isRequired;
  handleNumber = ctx: mkSimpleNode "number" ctx.description ctx.isRequired;
  handleString = ctx: mkSimpleNode "string" ctx.description ctx.isRequired;

  # creates a reference to the "AnyJSON" $ref
  handleAnyJson = ctx: {
    jsonschema = AnyJson // ctx.description;
    inherit (ctx) isRequired;
  };

  handleEnum =
    ctx:
    let
      typeName = ctx.getName ctx.args.typePrefix + lib.toSentenceCase ctx.args.mode;
      type = {
        enum = ctx.option.type.functor.payload.values;
      }
      // ctx.description;
    in
    {
      jsonschema = if ctx.args.shouldInlineTypes then type else ref typeName type;
      inherit (ctx) isRequired;
    };

  # ============================================================================
  # Main Conversion Functions
  # ============================================================================

  /**
    Takes a nix option and returns a node (or null) with this structure:

    ```nix
    {
      # jsonschema property this option generates
      property = {
        type = "boolean";
      }

      # If this option has a default value. It's used to decide when contained
      # in something that generates to an jsonschema object, its `required`
      # should contain the propery name that corresponds to this option.
      isRequired = true | false

      # Types that the node itself and its descendants generate, will be added
      # to the root $defs property of the jsonschema, omitted if it contains no
      # such types. Some example options that aways generate its own types:
      # attrsOf, listOf, submodule, etc
      defs = {
        InventoryInput = {
          type = "object";
          properties = {};
        };
        InventoryMachineOutput = {
          type = "object";
          properties = {};
        };
      }
    }
    ```
  */
  optionToNode =
    args@{

      typePrefix,
      mode,
      # Inside a branch of `eitehr` or input mode of `coercedTo`, types like
      # enum or one of shouldn't create a new type, because they might be merged
      # with other branches. only the outside type should create a new type.
      # But inside an attrs which is inside a branch, a custom type should be
      # created again;
      shouldInlineTypes ? false,
      typeRenames,
      ...
    }:
    option:
    let
      getName = finalName: typeRenames.${finalName} or finalName;
      isRequired = mode == "output" || !(option ? default) && !(option ? defaultText);
      description = lib.optionalAttrs (option ? description) {
        description = option.description.text or option.description;
      };

      ctx = {
        inherit
          args
          option
          isRequired
          description
          getName
          optionToNode
          optionsToNode
          ;
      };

      /**
        Returns true, if the passed node is one of the following:

        - array
        - object
        - enum
        - oneOf

        All other types return false
      */
      shouldDefineType =
        jsonschema:
        !shouldInlineTypes
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
    in
    if !isIncludedOption option then
      null
    else if isBoolOption option then
      handleBool ctx
    else if isIntOption option then
      handleInt ctx
    else if isFloatOption option then
      handleNumber ctx
    else if isStrOption option then
      handleString ctx
    else if isAnyOption option then
      handleAnyJson ctx
    else if option.type.name == "enum" then
      handleEnum ctx
    else if option.type.name == "nullOr" then
      let
        nestedOption = {
          type = option.type.nestedTypes.elemType;
          _type = "option";
          loc = option.loc;
        };
        node = optionToNode args nestedOption;
        oneOf = flattenOneOf (
          [
            { type = "null"; }
          ]
          ++ (lib.optional (node != null) node.jsonschema)
        );
        jsonschema =
          (
            if lib.length oneOf == 1 then
              lib.head oneOf
            else
              {
                inherit oneOf;
              }
          )
          // description;
      in
      {
        inherit jsonschema isRequired;
      }
    else if option.type.name == "either" then
      let
        nodesAttrs =
          lib.mapAttrs
            (
              name: type:
              optionToNode
                (
                  args
                  // {
                    typePrefix = getName (typePrefix + lib.optionalString (numOneOf >= 2) (lib.toSentenceCase name));
                    shouldInlineTypes = true;
                  }
                )
                {
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
        typeName = getName typePrefix + lib.toSentenceCase mode;
        jsonschema = (if numOneOf == 1 then lib.head oneOf else { inherit oneOf; }) // description;
      in
      if nodesAttrs.left == null && nodesAttrs.right == null then
        null
      else
        {
          jsonschema = if shouldDefineType jsonschema then ref typeName jsonschema else jsonschema;
          inherit isRequired;
        }
    else if option.type.name == "coercedTo" then
      let
        nodesAttrs =
          lib.mapAttrs
            (
              name: type:
              optionToNode
                (
                  args
                  // {
                    typePrefix = getName (typePrefix + lib.optionalString (numOneOf >= 2) (lib.toSentenceCase name));
                    shouldInlineTypes = mode == "input";
                  }
                )
                {
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
        typeName = getName typePrefix + lib.toSentenceCase mode;
      in
      # If this option can result in null for either input or output, it
      # shouldn't be included in either
      if nodesAttrs.from == null || nodesAttrs.to == null then
        null
      else
        {
          jsonschema =
            if mode == "input" && shouldDefineType jsonschema then ref typeName jsonschema else jsonschema;
          inherit isRequired;
        }
    else if option.type.name == "attrs" then
      let
        typeName = getName typePrefix + lib.toSentenceCase mode;
        jsonschema = {
          type = "object";
          additionalProperties = AnyJson;
        }
        // description;
      in
      {
        jsonschema = ref typeName jsonschema;
        inherit isRequired;
      }
    else if option.type.name == "submodule" then
      let
        subOptions = option.type.getSubOptions option.loc;
        node = optionsToNode (
          args
          // {
            submoduleInfo = {
              inherit isRequired;
            }
            // description;
          }
        ) subOptions;
      in
      node
    else if option.type.name == "listOf" then
      let
        nestedOption = {
          type = option.type.nestedTypes.elemType;
          _type = "option";
          loc = option.loc;
        };
        node = optionToNode (
          args
          // {
            typePrefix = getName (typePrefix + "Item");
            shouldInlineTypes = false;
          }
        ) nestedOption;
        typeName = getName typePrefix + lib.toSentenceCase mode;
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
        }
    else if option.type.name == "attrsOf" || option.type.name == "lazyAttrsOf" then
      let
        nestedOption = {
          type = option.type.nestedTypes.elemType;
          _type = "option";
          loc = option.loc;
        };
        node = optionToNode (
          args
          // {
            typePrefix = getName (typePrefix + "Item");
            shouldInlineTypes = false;
          }
        ) nestedOption;
        typeName = getName typePrefix + lib.toSentenceCase mode;
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
        }
    # throw error if option type is not supported
    else
      lib.trace option throw ''
        option type '${option.type.name}' ('${option.type.description}') not supported by jsonschema converter
        location: ${lib.concatStringsSep "." option.loc}
      '';
  /**
    Refer to `toOptionNode`'s doc for the definition of a node
  */
  optionsToNode =
    opts@{
      typePrefix,
      mode,
      typeRenames,
      submoduleInfo ? null,
      ...
    }:
    options:
    let
      getName = finalName: typeRenames.${finalName} or finalName;

      relevantOptions = removeAttrs options [
        "_module"
        "_freeformOptions"
      ];

      /**
        Map every option to a node
        Some options mapped to null get filtered out. i.e. those that are not "visible"
      */
      nodesAttrs = lib.filterAttrs (_: v: v != null) (
        lib.mapAttrs (
          name: option:
          let
            opts' = opts // {
              # We need to use toUpperFirst here because name might be "extraModules"
              # and we want to turn it into "ExtraModules", toSentenceCase turns it
              # to "Extramodules" which is not what we want
              typePrefix = getName (opts.typePrefix + clanLib.toUpperFirst name);
              shouldInlineTypes = false;
            };
          in
          if lib.isOption option then optionToNode opts' option else optionsToNode opts' option
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
          freeformOption = options._module.freeformType or null;
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
            opts
            // {
              typePrefix = getName (typePrefix + "Freeform");
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
          lib.optionalAttrs (opts.readOnly.${mode} or true) {
            readOnly = true;
          }
      ) nodesAttrs;

      required = lib.attrNames (lib.filterAttrs (_name: node: node.isRequired) nodesAttrs);
      typeName = getName typePrefix + lib.toSentenceCase mode;
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
        jsonschema = {
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
        defs = lib.concatMapAttrs (_name: result: result.defs) propsResults // additPropsResult.defs or { };
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
      typeRenames ? { },
    }:
    options:
    let
      inputNode = optionsToNode {
        mode = "input";
        inherit
          typePrefix
          readOnly
          typeRenames
          ;
      } options;
      inputResult = resolveRefs { } inputNode.jsonschema;
      outputNode = optionsToNode {
        mode = "output";
        inherit
          typePrefix
          readOnly
          typeRenames
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
