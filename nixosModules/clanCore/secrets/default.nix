{ config, lib, ... }:
{
  options.clanCore.secretStore = lib.mkOption {
    type = lib.types.enum [ "sops" "password-store" "custom" ];
    default = "sops";
    description = ''
      method to store secrets
      custom can be used to define a custom secret store.
      one would have to define system.clan.generateSecrets and system.clan.uploadSecrets
    '';
  };

  options.clanCore.secretsDirectory = lib.mkOption {
    type = lib.types.path;
    description = ''
      The directory where secrets are installed to. This is backend specific.
    '';
  };

  options.clanCore.secretsUploadDirectory = lib.mkOption {
    type = lib.types.nullOr lib.types.path;
    default = null;
    description = ''
      The directory where secrets are uploaded into, This is backend specific.
    '';
  };

  options.clanCore.secretsPrefix = lib.mkOption {
    type = lib.types.str;
    default = "";
    description = ''
      Prefix for secrets. This is backend specific.
    '';
  };

  options.clanCore.secrets = lib.mkOption {
    default = { };
    type = lib.types.attrsOf
      (lib.types.submodule (secret: {
        options = {
          name = lib.mkOption {
            type = lib.types.str;
            default = secret.config._module.args.name;
            description = ''
              Namespace of the secret
            '';
          };
          generator = lib.mkOption {
            type = lib.types.submodule ({ config, ... }: {
              options = {
                path = lib.mkOption {
                  type = lib.types.listOf (lib.types.either lib.types.path lib.types.package);
                  default = [ ];
                  description = ''
                    Extra paths to add to the PATH environment variable when running the generator.
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
                finalScript = lib.mkOption {
                  type = lib.types.str;
                  readOnly = true;
                  internal = true;
                  default = ''
                    export PATH="${lib.makeBinPath config.path}"
                    ${config.script}
                  '';
                };
              };
            });
          };
          secrets =
            let
              config' = config;
            in
            lib.mkOption {
              type = lib.types.attrsOf (lib.types.submodule ({ config, ... }: {
                options = {
                  name = lib.mkOption {
                    type = lib.types.str;
                    description = ''
                      name of the secret
                    '';
                    default = config._module.args.name;
                  };
                  path = lib.mkOption {
                    type = lib.types.str;
                    description = ''
                      path to a secret which is generated by the generator
                    '';
                    default = "${config'.clanCore.secretsDirectory}/${config'.clanCore.secretsPrefix}${config.name}";
                  };
                };
              }));
              description = ''
                path where the secret is located in the filesystem
              '';
            };
          facts = lib.mkOption {
            default = { };
            type = lib.types.attrsOf (lib.types.submodule (fact: {
              options = {
                name = lib.mkOption {
                  type = lib.types.str;
                  description = ''
                    name of the fact
                  '';
                  default = fact.config._module.args.name;
                };
                path = lib.mkOption {
                  type = lib.types.str;
                  description = ''
                    path to a fact which is generated by the generator
                  '';
                  default = "machines/${config.clanCore.machineName}/facts/${fact.config._module.args.name}";
                };
                value = lib.mkOption {
                  defaultText = lib.literalExpression "\${config.clanCore.clanDir}/\${fact.config.path}";
                  type = lib.types.nullOr lib.types.str;
                  default =
                    if builtins.pathExists "${config.clanCore.clanDir}/${fact.config.path}" then
                      lib.strings.removeSuffix "\n" (builtins.readFile "${config.clanCore.clanDir}/${fact.config.path}")
                    else
                      null;
                };
              };
            }));
          };
        };
      }));
  };
  imports = [
    ./sops.nix
    ./password-store.nix
  ];
}
