{ lib ? import <nixpkgs/lib> }:
let

  # from nixos type to jsonschema type
  typeMap = {
    bool = "boolean";
    float = "number";
    int = "integer";
    str = "string";
    path = "string"; # TODO add prober path checks
  };

  # remove _module attribute from options
  clean = opts: builtins.removeAttrs opts [ "_module" ];

  # throw error if option type is not supported
  notSupported = option: throw
    "option type '${option.type.description}' not supported by jsonschema converter";

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
      options = clean options';
      # parse options to jsonschema properties
      properties = lib.mapAttrs (_name: option: parseOption option) options;
      isRequired = prop: ! (prop ? default || prop.type == "object");
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

    # handle nested options (not a submodule)
    if ! option ? _type
    then parseOptions option

    # throw if not an option
    else if option._type != "option"
    then throw "parseOption: not an option"

    # parse nullOr
    else if option.type.name == "nullOr"
    # return jsonschema property definition for nullOr
    then default // description // {
      type = [
        "null"
        (typeMap.${option.type.functor.wrapped.name} or (notSupported option))
      ];
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
    else if option.type.name == "int"
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
    else if
      (option.type.name == "listOf")
      && (typeMap ? "${option.type.functor.wrapped.name}")
    # return jsonschema property definition for list
    then default // description // {
      type = "array";
      items = {
        type = typeMap.${option.type.functor.wrapped.name};
      };
    }

    # parse attrsOf submodule
    else if option.type.name == "attrsOf" && option.type.nestedTypes.elemType.name == "submodule"
    # return jsonschema property definition for attrsOf submodule
    then default // description // {
      type = "object";
      additionalProperties = parseOptions (option.type.nestedTypes.elemType.getSubOptions option.loc);
    }

    # parse attrs
    else if option.type.name == "attrsOf"
    # return jsonschema property definition for attrs
    then default // description // {
      type = "object";
      additionalProperties = {
        type = typeMap.${option.type.nestedTypes.elemType.name} or (notSupported option);
      };
    }

    # parse submodule
    else if option.type.name == "submodule"
    # return jsonschema property definition for submodule
    # then (lib.attrNames (option.type.getSubOptions option.loc).opt)
    then parseOptions (option.type.getSubOptions option.loc)

    # throw error if option type is not supported
    else notSupported option;
}
