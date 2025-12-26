# This module enables itself if
# manifest.features.API = true
# It converts the roles.interface to a json-schema
{ clanLib, prefix }:
{ lib, config, ... }:
{
  options.result.api = lib.mkOption {
    visible = false;
    default = { };
    type = lib.types.submodule ({
      options.schema = lib.mkOption {
        description = ''
          The API schema for configuring the service.

          Each 'role.<name>.interface' is converted to a json-schema.
          This can be used to generate and type check the API relevant objects.
        '';
        defaultText = lib.literalExpression ''
          {
            peer = { $schema" = "http://json-schema.org/<version>"; ... }
            commuter = { $schema" = "http://json-schema.org/<version>"; ... }
            distributor = { $schema" = "http://json-schema.org/<version>"; ... }
          }
        '';
        default = lib.mapAttrs (_roleName: v: clanLib.jsonschema.fromModule v.interface) config.roles;
      };
    });
  };

  config.result.assertions = (
    lib.mapAttrs' (roleName: _role: {
      name = "${roleName}";
      value = {
        # TODO: make the path to access the schema shorter
        message = ''
          `roles.${roleName}.interface` is not JSON serializable.

          'clan.services' modules require all 'roles.*.interfaces' to be subset of JSON.

          : clan.service module '${config.manifest.name}

          To see the evaluation problem run

          nix eval .#${lib.concatStringsSep "." prefix}.config.result.api.schema.${roleName}
        '';
        assertion = (builtins.tryEval (lib.deepSeq config.result.api.schema.${roleName} true)).success;
      };
    }) config.roles
  );

}
