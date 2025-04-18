{ config, lib, ... }:
{
  imports = [
    (lib.mkRemovedOptionModule [
      "clan"
      "core"
      "secretsPrefix"
    ] "secretsPrefix was only used by the sops module and the code is now integrated in there")
    (lib.mkRenamedOptionModule
      [
        "clan"
        "core"
        "secretStore"
      ]
      [
        "clan"
        "core"
        "facts"
        "secretStore"
      ]
    )
    (lib.mkRemovedOptionModule [
      "clan"
      "core"
      "secretsDirectory"
    ] "clan.core.secretsDirectory was removed. Use clan.core.facts.secretPathFunction instead")
    (lib.mkRenamedOptionModule
      [
        "clan"
        "core"
        "secretsUploadDirectory"
      ]
      [
        "clan"
        "core"
        "facts"
        "secretUploadDirectory"
      ]
    )
  ];
  options.clan.core.secrets = lib.mkOption {
    visible = false;
    default = { };
    type = lib.types.attrsOf (
      lib.types.submodule (service: {
        options = {
          name = lib.mkOption {
            type = lib.types.str;
            default = service.config._module.args.name;
            defaultText = "attribute name of the service";
            description = ''
              Namespace of the service
            '';
          };
          generator = lib.mkOption {
            type = lib.types.submodule (
              { ... }:
              {
                options = {
                  path = lib.mkOption {
                    type = lib.types.listOf (lib.types.either lib.types.path lib.types.package);
                    default = [ ];
                    description = ''
                      Extra paths to add to the PATH environment variable when running the generator.
                    '';
                  };
                  prompt = lib.mkOption {
                    type = lib.types.nullOr lib.types.str;
                    default = null;
                    description = ''
                      prompt text to ask for a value.
                      This value will be passed to the script as the environment variable $prompt_value.
                    '';
                  };
                  script = lib.mkOption {
                    type = lib.types.str;
                    description = ''
                      Script to generate the secret.
                      The script will be called with the following variables:
                      - facts: path to a directory where facts can be stored
                      - secrets: path to a directory where secrets can be stored
                      The script is expected to generate all secrets and facts defined in the module.
                    '';
                  };
                };
              }
            );
          };
          secrets = lib.mkOption {
            default = { };
            type = lib.types.attrsOf (
              lib.types.submodule (secret: {
                options =
                  {
                    name = lib.mkOption {
                      type = lib.types.str;
                      description = ''
                        name of the secret
                      '';
                      default = secret.config._module.args.name;
                      defaultText = "attribute name of the secret";
                    };
                    path = lib.mkOption {
                      type = lib.types.path;
                      description = ''
                        path to a secret which is generated by the generator
                      '';
                      default = config.clan.core.facts.secretPathFunction secret;
                      defaultText = lib.literalExpression "config.clan.core.facts.secretPathFunction secret";
                    };
                  }
                  // lib.optionalAttrs (config.clan.core.facts.secretStore == "sops") {
                    groups = lib.mkOption {
                      type = lib.types.listOf lib.types.str;
                      default = config.clan.core.sops.defaultGroups;
                      defaultText = lib.literalExpression "config.clan.core.sops.defaultGroups";
                      description = ''
                        Groups to decrypt the secret for. By default we always use the user's key.
                      '';
                    };
                  };
              })
            );
            description = ''
              path where the secret is located in the filesystem
            '';
          };
          facts = lib.mkOption {
            default = { };
            type = lib.types.attrsOf (
              lib.types.submodule (fact: {
                options = {
                  name = lib.mkOption {
                    type = lib.types.str;
                    description = ''
                      name of the fact
                    '';
                    default = fact.config._module.args.name;
                    defaultText = "attribute name of the fact";
                  };
                  path = lib.mkOption {
                    type = lib.types.path;
                    description = ''
                      path to a fact which is generated by the generator
                    '';
                    default =
                      config.clan.core.settings.directory
                      + "/machines/${config.clan.core.settings.machine.name}/facts/${fact.config._module.args.name}";
                    defaultText = lib.literalExpression "\${config.clan.core.settings.directory}/machines/\${config.clan.core.settings.machine.name}/facts/\${fact.config._module.args.name}";
                  };
                  value = lib.mkOption {
                    type = lib.types.nullOr lib.types.str;
                    default =
                      if builtins.pathExists fact.config.path then lib.strings.fileContents fact.config.path else null;
                    defaultText = "null if fact.config.path does not exist, else the content of the file";
                  };
                };
              })
            );
          };
        };
      })
    );
  };
  config = lib.mkIf (config.clan.core.secrets != { }) {
    clan.core.facts.services = lib.mapAttrs' (
      name: service:
      lib.warn "clan.core.secrets.${name} is deprecated, use clan.core.facts.services.${name} instead" (
        lib.nameValuePair name ({
          secret = service.secrets;
          public = service.facts;
          generator = service.generator;
        })
      )
    ) config.clan.core.secrets;
  };
}
