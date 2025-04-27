# This module enables itself if
# manifest.features.API = true
# It converts the roles.interface to a json-schema
{ clanLib }:
let
  converter = clanLib.jsonschema {
    includeDefaults = true;
  };
in
{ lib, config, ... }:
{
  options.result.api = lib.mkOption {
    default = { };
    type = lib.types.submodule (
      lib.optionalAttrs config.manifest.features.API {
        options.schema = lib.mkOption {
          description = ''
            The API schema for configuring the service.

            Each 'role.<name>.interface' is converted to a json-schema.
            This can be used to generate and type check the API relevant objects.
          '';
          defaultText = lib.literalExpression ''
            {
              peer = { $schema" = "http://json-schema.org/draft-07/schema#"; ... }
              commuter = { $schema" = "http://json-schema.org/draft-07/schema#"; ... }
              distributor = { $schema" = "http://json-schema.org/draft-07/schema#"; ... }
            }
          '';
          default = lib.mapAttrs (_roleName: v: converter.parseModule v.interface) config.roles;
        };
      }
    );
  };
}
