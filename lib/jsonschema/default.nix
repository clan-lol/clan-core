{
  lib ? import <nixpkgs/lib>,
  clanLib,
}:
let
  refPrefix = "#/$defs/";
  ref = typeName: {
    "$ref" = refPrefix + typeName;
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
        items = ref "AnyJson";
      }
      {
        type = "object";
        additionalProperties = ref "AnyJson";
      }
    ];
  };
  flattenOneOf = import ./flattenOneOf.nix {
    inherit lib clanLib;
  };
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
  toOptionNode =
    opts@{
      typePrefix,
      mode,
      excludedTypes,
      # Inside a branch of `eitehr` or input mode of `coercedTo`, types like
      # enum or one of shouldn't create a new type, because they might be merged
      # with other branches. only the outside type should create a new type.
      # But inside an attrs which is inside a branch, a custom type should be
      # created again;
      isDirectlyInsideBranch ? false,
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
    in
    if !isIncludedOption excludedTypes option then
      null
    else if isBoolOption option then
      {
        property = {
          type = "boolean";
        }
        // description;
        inherit isRequired;
      }
    else if isIntOption option then
      {
        property = {
          type = "integer";
        }
        // description;
        inherit isRequired;
      }
    else if isFloatOption option then
      {
        property = {
          type = "number";
        }
        // description;
        inherit isRequired;
      }
    else if isStrOption option then
      {
        property = {
          type = "string";
        }
        // description;
        inherit isRequired;
      }
    else if isAnyOption option then
      {
        property = ref "AnyJson" // description;
        inherit isRequired;
        defs = {
          inherit AnyJson;
        };
      }
    else if option.type.name == "enum" then
      let
        typeName = getName typePrefix;
        type = {
          enum = option.type.functor.payload.values;
        }
        // description;
        defs =
          if isDirectlyInsideBranch then
            { }
          else
            {
              ${typeName} = type;
            };
      in
      {
        property = if isDirectlyInsideBranch then type else ref typeName;
        inherit isRequired;
      }
      // lib.optionalAttrs (defs != { }) {
        defs = defs;
      }
    else if option.type.name == "nullOr" then
      let
        nestedOption = {
          type = option.type.nestedTypes.elemType;
          _type = "option";
          loc = option.loc;
        };
        node = toOptionNode opts nestedOption;
        inherit
          (flattenOneOf node.defs or { } (
            [
              { type = "null"; }
            ]
            ++ (lib.optional (node != null) node.property)
          ))
          oneOf
          defs
          ;
        property =
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
        inherit property isRequired;
      }
      // lib.optionalAttrs (defs != { }) {
        defs = defs;
      }
    else if option.type.name == "either" then
      let
        nodesAttrs =
          lib.mapAttrs
            (
              name: type:
              toOptionNode
                (
                  opts
                  // {
                    typePrefix = typePrefix + lib.toSentenceCase name;
                    isDirectlyInsideBranch = true;
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
        inherit
          (flattenOneOf (lib.concatMapAttrs (_name: node: node.defs or { }) nodesAttrs) (
            map (node: node.property) nodes
          ))
          oneOf
          defs
          ;
        numOneOf = lib.length oneOf;
        typeName =
          getName typePrefix + (lib.toSentenceCase mode);
        property = (if numOneOf == 1 then lib.head oneOf else { inherit oneOf; }) // description;
        createsTypeName = !isDirectlyInsideBranch && shouldCreateTypeName property;
        defs' =
          defs
          // lib.optionalAttrs createsTypeName {
            ${typeName} = property;
          };
      in
      if nodesAttrs.left == null && nodesAttrs.right == null then
        null
      else
        {
          property = if createsTypeName then ref typeName else property;
          inherit isRequired;
        }
        // lib.optionalAttrs (defs' != { }) {
          defs = defs';
        }
    else if option.type.name == "coercedTo" then
      let
        nodesAttrs =
          lib.mapAttrs
            (
              name: type:
              toOptionNode
                (
                  opts
                  // {
                    typePrefix = typePrefix + lib.toSentenceCase name;
                    isDirectlyInsideBranch = mode == "input";
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
        typeName =
          getName typePrefix
          + lib.toSentenceCase mode;
      in
      # If this option can result in null for either input or output, it
      # shouldn't be included in either
      if nodesAttrs.from == null || nodesAttrs.to == null then
        null
      else if mode == "input" then
        let
          inherit
            (flattenOneOf (lib.concatMapAttrs (_name: node: node.defs or { }) nodesAttrs) (
              map (node: node.property) nodes
            ))
            oneOf
            defs
            ;
          numOneOf = lib.length oneOf;
          property =
            (
              if numOneOf == 1 then
                lib.head oneOf
              else
                {
                  inherit oneOf;
                }
            )
            // description;
          createsTypeName = shouldCreateTypeName property;
          defs' =
            defs
            // lib.optionalAttrs createsTypeName {
              ${typeName} = property;
            };
        in
        {
          property = if createsTypeName then ref typeName else property;
          inherit isRequired;
        }
        // lib.optionalAttrs (defs' != { }) {
          defs = defs';
        }
      else
        let
          node = nodesAttrs.to;
        in
        {
          property = node.property // description;
          inherit isRequired;
        }
        // lib.optionalAttrs (node ? defs) {
          defs = node.defs;
        }
    else if option.type.name == "attrs" then
      let
        typeName = getName typePrefix;
      in
      {
        property = ref typeName;
        inherit isRequired;
        defs = {
          ${typeName} = {
            type = "object";
            additionalProperties = ref "AnyJson";
          }
          // description;
          inherit AnyJson;
        };
      }
    else if option.type.name == "submodule" then
      let
        subOptions = option.type.getSubOptions option.loc;
        node = toOptionsNode (opts // { inherit description; }) subOptions;
      in
      node
    else if option.type.name == "listOf" then
      let
        nestedOption = {
          type = option.type.nestedTypes.elemType;
          _type = "option";
          loc = option.loc;
        };
        node = toOptionNode (
          opts
          // {
            typePrefix = getName (typePrefix + "Item");
            isDirectlyInsideBranch = false;
          }
        ) nestedOption;
        typeName =
          getName typePrefix

          + (lib.toSentenceCase mode);
      in
      if node == null then
        null
      else
        {
          property = ref typeName;
          inherit isRequired;
          defs = node.defs or { } // {
            ${typeName} = {
              type = "array";
              items = node.property;
            }
            // description;
          };
        }
    else if option.type.name == "attrsOf" || option.type.name == "lazyAttrsOf" then
      let
        nestedOption = {
          type = option.type.nestedTypes.elemType;
          _type = "option";
          loc = option.loc;
        };
        node = toOptionNode (
          opts
          // {
            typePrefix = getName (typePrefix + "Item");
            isDirectlyInsideBranch = false;
          }
        ) nestedOption;
        typeName =
          getName typePrefix

          + (lib.toSentenceCase mode);
      in
      if node == null then
        null
      else
        {
          property = ref typeName;
          inherit isRequired;
          defs = node.defs or { } // {
            ${typeName} = {
              type = "object";
              additionalProperties = node.property;
            }
            // description;
          };
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
  toOptionsNode =
    opts@{
      typePrefix,
      mode,
      typeRenames,
      # A submodule can provide this value
      description ? { },
      ...
    }:
    options:
    let
      getName = finalName: typeRenames.${finalName} or finalName;

      nodesAttrs = lib.filterAttrs (n: v: v != null) (
        lib.mapAttrs (
          name: option:
          if
            builtins.elem name [
              "_module"
              "_freeformOptions"
            ]
          then
            null
          else if lib.isOption option then
            toOptionNode (
              opts
              // {
                typePrefix = getName (typePrefix + lib.toSentenceCase name);
                isDirectlyInsideBranch = false;
              }
            ) option
          else
            # handle nested options (not a submodule)
            # foo.bar = mkOption { type = str; };
            toOptionsNode (
              opts
              // {
                typePrefix = getName (typePrefix + lib.toSentenceCase name);
                isDirectlyInsideBranch = false;
              }
            ) option
        ) options
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
          toOptionNode (
            opts
            // {
              typePrefix = getName typePrefix;
            }
          ) nestedOption;
      properties = lib.mapAttrs (_name: node: node.property // readOnly) nodesAttrs;
      # TODO: readOnly has no effect here becaus datamodel-code-generator's
      # --use-frozen-field flag doesn't support TypedDict yet. when it doesn,
      # this should generate typing.ReadOnly, and will allow assigning an output
      # type to the corresponding input type. Currently it will complain that a
      # required property can not be passed to a non-required one.
      # We do this in the unit tests:
      #   machine_jon = get_machine(flake, "jon")
      #   set_machine(Machine("jon", flake), machine_jon)
      readOnly = lib.optionalAttrs (opts.readOnly.${mode} or true) {
        readOnly = true;
      };
      required = lib.attrNames (lib.filterAttrs (_name: node: node.isRequired) nodesAttrs);
      typeName = typePrefix + lib.toSentenceCase mode;
    in
    if nodesAttrs == { } && freeformNode == null then
      {
        property = {
          type = "object";
          additionalProperties = false;
        };
        # FIXME: shouldn't this depend on the default value of the submodule itself?
        isRequired = false;
      }
      // lib.optionalAttrs (freeformNode ? defs) {
        defs = freeformNode.defs;
      }
    else
      {
        property = ref typeName;
        # This property is required if none of its child properties has a
        # default value (i.e., some of its child property's isRequired is true)
        isRequired = required != [ ];

        # We always different types for input and output for options, to make
        # the types stable.
        #
        # For example:
        #   foo.bar = mkOption { type = bool; }
        #   foo.baz = mkOption { type = bool; }
        #
        # In this case, both bar and nd baz are of simple types and foo can be
        # of the same type for both input and output. Later, if a new coercedTo
        # option is added, the type has to be split, having different names in
        # input and output. This breaks existing code that uses the old type.
        defs = {
          ${typeName} = {
            type = "object";
            additionalProperties = if freeformNode == null then false else freeformNode.property;
            # Make sure to not add readOnly here
            # a property should only have readOnly if it's a direct child of an
            # object, by itself it doesn't know if that's the case;
          }
          // description
          // lib.optionalAttrs (properties != { }) {
            inherit properties;
          }
          // lib.optionalAttrs (required != [ ]) {
            inherit required;
          };
        }
        # Freeform type has a lower priority because a user might
        # rename it to an existing type, in which case the existing type should
        # be kept because a freeform type is less likely to have a description
        // freeformNode.defs or { }
        // lib.concatMapAttrs (_name: node: node.defs or { }) nodesAttrs;
      };

  isIncludedOption =
    excludedTypes: option: option.visible or true && !lib.elem (option.type.name or null) excludedTypes;
  isBoolOption =
    option:
    {
      bool = true;
      boolByOr = true;
    }
    .${option.type.name} or false;
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
  isFloatOption =
    option:
    {
      float = true;
      numberBetween = true;
      numberNonnegative = true;
      numberPositive = true;
    }
    .${option.type.name} or false;
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
  shouldCreateTypeName =
    property:
    (
      property ? type
      && lib.elem property.type [
        "array"
        "object"
      ]
    )
    || property ? enum
    || property ? oneOf;
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
      excludedTypes ? [
        "functionTo"
        "package"
      ],
    }:
    options:
    let
      inputNode = toOptionsNode {
        mode = "input";
        inherit
          typePrefix
          readOnly
          excludedTypes
          typeRenames
          ;
      } options;
      outputNode = toOptionsNode {
        mode = "output";
        inherit
          typePrefix
          readOnly
          excludedTypes
          typeRenames
          ;
      } options;
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
      "$defs" =
        lib.optionalAttrs input inputNode.defs or { } // lib.optionalAttrs output outputNode.defs or { };
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
