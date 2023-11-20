{ lib ? import <nixpkgs/lib>
, excludedTypes ? [
    "functionTo"
    "package"
  ]
}:
let
  # remove _module attribute from options
  clean = opts: builtins.removeAttrs opts [ "_module" ];

  # throw error if option type is not supported
  notSupported = option: lib.trace option throw ''
    option type '${option.type.name}' ('${option.type.description}') not supported by jsonschema converter
    location: ${lib.concatStringsSep "." option.loc}
  '';

  isExcludedOption = option: (lib.elem (option.type.name or null) excludedTypes);

  filterExcluded = lib.filter (opt: ! isExcludedOption opt);

  filterExcludedAttrs = lib.filterAttrs (_name: opt: ! isExcludedOption opt);

  allBasicTypes =
    [ "boolean" "integer" "number" "string" "array" "object" "null" ];

in
rec {

  # parses a nixos module to a jsonschema
  parseModule = module:
    let
      evaled = lib.evalModules {
        modules = [ module ];
      };
    in
    parseOptions evaled.options;

  # parses a set of evaluated nixos options to a jsonschema
  parseOptions = options':
    let
      options = filterExcludedAttrs (clean options');
      # parse options to jsonschema properties
      properties = lib.mapAttrs (_name: option: parseOption option) options;
      # TODO: figure out how to handle if prop.anyOf is used
      isRequired = prop: ! (prop ? default || prop.type or null == "object");
      requiredProps = lib.filterAttrs (_: prop: isRequired prop) properties;
      required = lib.optionalAttrs (requiredProps != { }) {
        required = lib.attrNames requiredProps;
      };
    in
    # return jsonschema
    required // {
      type = "object";
      inherit properties;
    };

  # parses and evaluated nixos option to a jsonschema property definition
  parseOption = option:
    let
      default = lib.optionalAttrs (option ? default) {
        inherit (option) default;
      };
      description = lib.optionalAttrs (option ? description) {
        inherit (option) description;
      };
    in

    # either type
      # TODO: if all nested optiosn are excluded, the parent sould be excluded too
    if option.type.name or null == "either"
    # return jsonschema property definition for either
    then
      let
        optionsList' = [
          { type = option.type.nestedTypes.left; _type = "option"; loc = option.loc; }
          { type = option.type.nestedTypes.right; _type = "option"; loc = option.loc; }
        ];
        optionsList = filterExcluded optionsList';
      in
      default // description // {
        anyOf = map parseOption optionsList;
      }

    # handle nested options (not a submodule)
    else if ! option ? _type
    then parseOptions option

    # throw if not an option
    else if option._type != "option" && option._type != "option-type"
    then throw "parseOption: not an option"

    # parse nullOr
    else if option.type.name == "nullOr"
    # return jsonschema property definition for nullOr
    then
      let
        nestedOption =
          { type = option.type.nestedTypes.elemType; _type = "option"; loc = option.loc; };
      in
      default // description // {
        anyOf =
          [{ type = "null"; }]
          ++ (
            lib.optional (! isExcludedOption nestedOption)
              (parseOption nestedOption)
          );
      }

    # parse bool
    else if option.type.name == "bool"
    # return jsonschema property definition for bool
    then default // description // {
      type = "boolean";
    }

    # parse float
    else if option.type.name == "float"
    # return jsonschema property definition for float
    then default // description // {
      type = "number";
    }

    # parse int
    else if (option.type.name == "int" || option.type.name == "positiveInt")
    # return jsonschema property definition for int
    then default // description // {
      type = "integer";
    }

    # parse string
    else if option.type.name == "str"
    # return jsonschema property definition for string
    then default // description // {
      type = "string";
    }

    # parse string
    else if option.type.name == "path"
    # return jsonschema property definition for path
    then default // description // {
      type = "string";
    }

    # parse anything
    else if option.type.name == "anything"
    # return jsonschema property definition for anything
    then default // description // {
      type = allBasicTypes;
    }

    # parse unspecified
    else if option.type.name == "unspecified"
    # return jsonschema property definition for unspecified
    then default // description // {
      type = allBasicTypes;
    }

    # parse raw
    else if option.type.name == "raw"
    # return jsonschema property definition for raw
    then default // description // {
      type = allBasicTypes;
    }

    # parse enum
    else if option.type.name == "enum"
    # return jsonschema property definition for enum
    then default // description // {
      enum = option.type.functor.payload;
    }

    # parse listOf submodule
    else if option.type.name == "listOf" && option.type.functor.wrapped.name == "submodule"
    # return jsonschema property definition for listOf submodule
    then default // description // {
      type = "array";
      items = parseOptions (option.type.functor.wrapped.getSubOptions option.loc);
    }

    # parse list
    else if (option.type.name == "listOf")
    # return jsonschema property definition for list
    then
      let
        nestedOption = { type = option.type.functor.wrapped; _type = "option"; loc = option.loc; };
      in
      default // description // {
        type = "array";
        items = parseOption nestedOption;
      }

    # parse list of unspecified
    else if
      (option.type.name == "listOf")
      && (option.type.functor.wrapped.name == "unspecified")
    # return jsonschema property definition for list
    then default // description // {
      type = "array";
    }

    # parse attrsOf submodule
    else if option.type.name == "attrsOf" && option.type.nestedTypes.elemType.name == "submodule"
    # return jsonschema property definition for attrsOf submodule
    then default // description // {
      type = "object";
      additionalProperties = parseOptions (option.type.nestedTypes.elemType.getSubOptions option.loc);
    }

    # parse attrs
    else if option.type.name == "attrs"
    # return jsonschema property definition for attrs
    then default // description // {
      type = "object";
      additionalProperties = true;
    }

    # parse attrsOf
    # TODO: if nested option is excluded, the parent sould be excluded too
    else if option.type.name == "attrsOf" || option.type.name == "lazyAttrsOf"
    # return jsonschema property definition for attrs
    then
      let
        nestedOption = { type = option.type.nestedTypes.elemType; _type = "option"; loc = option.loc; };
      in
      default // description // {
        type = "object";
        additionalProperties =
          if ! isExcludedOption nestedOption
          then parseOption { type = option.type.nestedTypes.elemType; _type = "option"; loc = option.loc; }
          else false;
      }

    # parse submodule
    else if option.type.name == "submodule"
    # return jsonschema property definition for submodule
    # then (lib.attrNames (option.type.getSubOptions option.loc).opt)
    then parseOptions (option.type.getSubOptions option.loc)

    # throw error if option type is not supported
    else notSupported option;
}
