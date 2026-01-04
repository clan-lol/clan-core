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

      # If the type is only a simple type like string, bool or a listOf
      # or attrsOf containing a simple type, generate the same type for input
      # and output
      isSameInputOutputType = true | false

      # Types that the node itself and its descendants generate, will be added
      # to the root $defs property of the jsonschema, omitted if it contains no
      # such types. Some example options that aways generate its own types:
      # attrsOf, listOf, submodule, etc
      descendantAndSelfTypes = {
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
      # Inside coercedTo, all custom types need the input/output suffix,
      # because they won't share the types
      isInsideCoercedTo,
      renameType,
      ...
    }:
    option:
    let
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
        isSameInputOutputType = true;
      }
    else if isIntOption option then
      {
        property = {
          type = "integer";
        }
        // description;
        inherit isRequired;
        isSameInputOutputType = true;
      }
    else if isFloatOption option then
      {
        property = {
          type = "number";
        }
        // description;
        inherit isRequired;
        isSameInputOutputType = true;
      }
    else if isStrOption option then
      {
        property = {
          type = "string";
        }
        // description;
        inherit isRequired;
        isSameInputOutputType = true;
      }
    else if isAnyOption option then
      {
        property = ref "AnyJson" // description;
        inherit isRequired;
        isSameInputOutputType = true;
        descendantAndSelfTypes = {
          inherit AnyJson;
        };
      }
    else if option.type.name == "enum" then
      let
        typeName = typePrefix + lib.optionalString isInsideCoercedTo (clanLib.toUpperFirst mode);
      in
      {
        property = ref typeName;
        inherit isRequired;
        isSameInputOutputType = true;
        descendantAndSelfTypes = {
          ${typeName} = {
            enum = option.type.functor.payload.values;
          }
          // description;
        };
      }
    else if option.type.name == "nullOr" then
      let
        nestedOption = {
          type = option.type.nestedTypes.elemType;
          _type = "option";
          loc = option.loc;
        };
        node = toOptionNode opts nestedOption;
        oneOf = flattenOneOf descendantTypes (
          [
            { type = "null"; }
          ]
          ++ (lib.optional (node != null) node.property)
        );
        descendantTypes = node.descendantAndSelfTypes or { };
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
        isSameInputOutputType = if node == null then true else node.isSameInputOutputType;
      }
      // lib.optionalAttrs (descendantTypes != { }) {
        descendantAndSelfTypes = descendantTypes;
      }
    else if option.type.name == "either" then
      let
        nodesAttrs =
          lib.mapAttrs
            (
              _name: type:
              # TODO: For a case like `either submodule str`, the `submodule`
              # part should also result in its own type name, in which case
              # users are supposed to replace it so it doesn't collide with
              # `either`'s type name. We need to support:
              #
              # opts // { typePrefix = renameType { loc = "either"; ... }; }
              #
              # Need to think about how to let users know which branch they are
              # in.
              toOptionNode opts {
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
        oneOf = flattenOneOf descendantTypes (map (node: node.property) nodes);
        numOneOf = lib.length oneOf;
        isSameInputOutputType = lib.all (node: node.isSameInputOutputType) nodes;
        typeName =
          typePrefix
          + lib.optionalString (isInsideCoercedTo || !isSameInputOutputType) (clanLib.toUpperFirst mode);
        descendantTypes = lib.concatMapAttrs (_name: node: node.descendantAndSelfTypes or { }) nodesAttrs;
        descendantAndSelfTypes =
          descendantTypes
          // lib.optionalAttrs (numOneOf >= 2) {
            ${typeName} = {
              inherit oneOf;
            }
            // description;
          };
      in
      if nodesAttrs.left == null && nodesAttrs.right == null then
        null
      else
        {
          property = if numOneOf == 1 then (lib.head oneOf) // description else ref typeName;
          inherit isRequired isSameInputOutputType;
        }
        // lib.optionalAttrs (descendantAndSelfTypes != { }) {
          inherit descendantAndSelfTypes;
        }
    else if option.type.name == "coercedTo" then
      let
        nodesAttrs =
          lib.mapAttrs
            (
              _name: type:
              # TODO: For a case like `coercedTo submodule (...) str`, the
              # `submodule` part should also result in its own type name, in
              # which case users are supposed to replace it so it doesn't
              # collide with `either`'s type name. We need to support:
              #
              # opts // { typePrefix = renameType { loc = "coercedTo"; ... }; }
              #
              # Need to think about how to let users know which branch they are
              # in.
              toOptionNode (opts // { isInsideCoercedTo = true; }) {
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
        typeName = typePrefix + clanLib.toUpperFirst mode;
      in
      # If this option can result in null for either input or output, it
      # shouldn't be included in either
      if nodesAttrs.from == null || nodesAttrs.to == null then
        null
      else if mode == "input" then
        let
          oneOf = flattenOneOf descendantTypes (map (node: node.property) nodes);
          numOneOf = lib.length oneOf;
          descendantTypes = lib.concatMapAttrs (_name: node: node.descendantAndSelfTypes or { }) nodesAttrs;
          descendantAndSelfTypes =
            descendantTypes
            // lib.optionalAttrs (numOneOf >= 2) {
              ${typeName} = {
                inherit oneOf;
              }
              // description;
            };
        in
        {
          property = if numOneOf == 1 then lib.head oneOf // description else ref typeName;
          inherit isRequired;
          isSameInputOutputType = false;
        }
        // lib.optionalAttrs (descendantAndSelfTypes != { }) {
          inherit descendantAndSelfTypes;
        }
      else
        let
          node = nodesAttrs.to;
        in
        {
          property = node.property // description;
          inherit isRequired;
          isSameInputOutputType = false;
        }
        // lib.optionalAttrs (node ? descendantAndSelfTypes) {
          descendantAndSelfTypes = node.descendantAndSelfTypes;
        }
    else if option.type.name == "attrs" then
      let
        typeName = typePrefix + lib.optionalString isInsideCoercedTo (clanLib.toUpperFirst mode);
      in
      {
        property = ref typeName;
        inherit isRequired;
        isSameInputOutputType = true;
        descendantAndSelfTypes = {
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
            typePrefix = renameType {
              loc = "listOfItem";
              name = typePrefix;
            };
          }
        ) nestedOption;
        isSameInputOutputType = node.isSameInputOutputType;
        typeName =
          typePrefix
          + lib.optionalString (isInsideCoercedTo || !isSameInputOutputType) (clanLib.toUpperFirst mode);
      in
      if node == null then
        null
      else
        {
          property = ref typeName;
          inherit isRequired isSameInputOutputType;
          descendantAndSelfTypes = node.descendantAndSelfTypes or { } // {
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
            typePrefix = renameType {
              loc = "attrsOfItem";
              name = typePrefix;
            };
          }
        ) nestedOption;
        isSameInputOutputType = node.isSameInputOutputType;
        typeName =
          typePrefix
          + lib.optionalString (isInsideCoercedTo || !isSameInputOutputType) (clanLib.toUpperFirst mode);
      in
      if node == null then
        null
      else
        {
          property = ref typeName;
          inherit isRequired isSameInputOutputType;
          descendantAndSelfTypes = node.descendantAndSelfTypes or { } // {
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
      renameType,
      addsKeysType,
      # A submodule can provide this value
      description ? { },
      ...
    }:
    options:
    let
      nodesAttrs =
        lib.concatMapAttrs
          (
            name: option:
            if option ? _type then
              let
                node = toOptionNode (
                  opts
                  // {
                    typePrefix = renameType {
                      loc = "submodule";
                      name = typePrefix + clanLib.toUpperFirst name;
                    };
                  }
                ) option;
              in
              lib.optionalAttrs (node != null) ({
                ${name} = node;
              })
            else
              # handle nested options (not a submodule)
              # foo.bar = mkOption { type = str; };
              let
                node = toOptionsNode (
                  opts
                  // {
                    typePrefix = renameType {
                      loc = "optionPath";
                      name = typePrefix + clanLib.toUpperFirst name;
                    };
                  }
                ) option;
              in
              {
                ${name} = node;
              }
          )
          (
            lib.removeAttrs options [
              "_module"
              "_freeformOptions"
            ]
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
              typePrefix = renameType {
                loc = "freeform";
                name = typePrefix;
              };
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
      typeName = typePrefix + clanLib.toUpperFirst mode;
    in
    if nodesAttrs == { } && freeformNode == null then
      null
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
        isSameInputOutputType = false;
        descendantAndSelfTypes = {
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
        // lib.concatMapAttrs (_name: node: node.descendantAndSelfTypes or { }) nodesAttrs
        // freeformNode.descendantAndSelfTypes or { }
        // lib.optionalAttrs (addsKeysType && properties != { }) {
          "${typeName}Keys" = {
            enum = lib.attrNames properties;
          };
        };
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
  flattenOneOf =
    descendantTypes: types:
    let
      flatten =
        flattened: types:
        lib.foldl' (
          flattened: type: if type ? oneOf then flatten flattened type.oneOf else mergeType flattened type
        ) flattened types;
      mergeType =
        types: newType:
        let
          containingIndex = lib.lists.findFirstIndex (
            existingType: isContainingType existingType newType
          ) null types;
          containedIndex = lib.lists.findFirstIndex (
            existingType: isContainingType newType existingType
          ) null types;
        in
        if containingIndex != null then
          types
        else if containedIndex != null then
          lib.take containedIndex types ++ [ newType ] ++ lib.drop (containedIndex + 1) types
        else
          types ++ [ newType ];
      isContainingType =
        t1: t2:
        let
          attrStatus =
            attrName:
            if lib.hasAttr attrName t1 then
              if lib.hasAttr attrName t2 then "bothHave" else "oneHas"
            else if lib.hasAttr attrName t2 then
              "oneHas"
            else
              "neitherHas";
          isContainingAttr =
            attrName:
            let
              status = attrStatus attrName;
            in
            status == "bothHave" && isContainingType t1.${attrName} t2.${attrName} || status == "neitherHas";
          isContainingAttrs =
            attrName:
            let
              status = attrStatus attrName;
            in
            status == "bothHave"
            && lib.all (
              name:
              if !(lib.hasAttr name t1.${attrName}) then
                false
              else
                isContainingType t1.${attrName}.${name} t2.${attrName}.${name}
            ) (lib.attrNames t2.${attrName})
            || status == "neitherHas";
          isSameAttrValue =
            attrName:
            let
              status = attrStatus attrName;
            in
            status == "bothHave" && t1.${attrName} == t2.${attrName} || status == "neitherHas";
          derefType = type: descendantTypes.${lib.removePrefix refPrefix type."$ref"};
          attrTypeStatus = attrStatus "type";
          attrEnumStatus = attrStatus "enum";
        in
        if !isSameAttrValue "readOnly" then
          false
        else if t1 ? "$ref" then
          isContainingType (derefType t1) t2
        else if t2 ? "$ref" then
          isContainingType t1 (derefType t2)
        else if t1 ? oneOf && t2 ? oneOf then
          lib.all (branch2: lib.any (branch1: isContainingType branch1 branch2) t1.oneOf) t2.oneOf
        else if t1 ? oneOf then
          lib.any (branch: isContainingType branch t2) t1.oneOf
        else if attrTypeStatus == "bothHave" then
          if t1.type != t2.type then
            false
          else if t1.type == "array" then
            isContainingAttr "items" && isContainingAttr "prefixItems"
          else if t1.type == "object" then
            isContainingAttrs "properties"
            && isSameAttrValue "required"
            && isContainingAttr "additionalProperties"
          else
            true
        else if attrTypeStatus == "oneHas" then
          false
        else if attrEnumStatus == "bothHave" then
          lib.all (item: lib.elem item t1.enum) t2.enum
        else if attrEnumStatus == "oneHas" then
          false
        else
          false;
    in
    flatten [ ] types;
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
      addsKeysType ? true,
      renameType ? { name, ... }: name,
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
          addsKeysType
          excludedTypes
          renameType
          ;
        isInsideCoercedTo = false;
      } options;
      outputNode = toOptionsNode {
        mode = "output";
        inherit
          typePrefix
          readOnly
          addsKeysType
          excludedTypes
          renameType
          ;
        isInsideCoercedTo = false;
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
        lib.optionalAttrs input inputNode.descendantAndSelfTypes or { }
        // lib.optionalAttrs output outputNode.descendantAndSelfTypes or { };
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
