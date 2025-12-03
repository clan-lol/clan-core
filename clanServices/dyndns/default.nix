{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/dyndns";
  manifest.description = "A dynamic DNS service to auto update domain IPs";
  manifest.categories = [ "Network" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.default = {
    description = "Placeholder role to apply the dyndns service";
    interface =
      { lib, ... }:
      {
        options = {
          server = {
            enable = lib.mkEnableOption "dyndns webserver";
            domain = lib.mkOption {
              type = lib.types.str;
              description = "Domain to serve the webservice on";
            };
            port = lib.mkOption {
              type = lib.types.int;
              default = 54805;
              description = "Port to listen on";
            };
            acmeEmail = lib.mkOption {
              type = lib.types.str;
              description = ''
                Email address for account creation and correspondence from the CA.
                It is recommended to use the same email for all certs to avoid account
                creation limits.
              '';
            };
          };

          period = lib.mkOption {
            type = lib.types.int;
            default = 5;
            description = "Domain update period in minutes";
          };

          settings = lib.mkOption {
            type = lib.types.attrsOf (
              lib.types.submodule (
                { ... }:
                {
                  options = {
                    provider = lib.mkOption {
                      example = "namecheap";
                      type = lib.types.str;
                      description = "The dyndns provider to use";
                    };
                    domain = lib.mkOption {
                      type = lib.types.str;
                      example = "example.com";
                      description = "The top level domain to update.";
                    };
                    secret_field_name = lib.mkOption {
                      example = "api_key";

                      type = lib.types.enum [
                        "password"
                        "token"
                        "api_key"
                        "secret_api_key"
                      ];
                      default = "password";
                      description = "The field name for the secret";
                    };
                    extraSettings = lib.mkOption {
                      type = lib.types.attrsOf lib.types.str;
                      default = { };
                      description = ''
                        Extra settings for the provider.
                        Provider specific settings: https://github.com/qdm12/ddns-updater#configuration
                      '';
                    };
                  };
                }
              )
            );
            default = { };
            description = "Configuration for which domains to update";
          };
        };
      };

    perInstance =
      { settings, ... }:
      {
        nixosModule =
          {
            config,
            lib,
            pkgs,
            ...
          }:
          let
            name = "dyndns";
            cfg = settings;

            # We dedup secrets if they have the same provider + base domain
            secret_id = opt: "${name}-${opt.provider}-${opt.domain}";
            secret_path =
              opt: config.clan.core.vars.generators."${secret_id opt}".files."${secret_id opt}".path;

            # We check that a secret has not been set in extraSettings.
            extraSettingsSafe =
              opt:
              if (builtins.hasAttr opt.secret_field_name opt.extraSettings) then
                throw "Please do not set ${opt.secret_field_name} in extraSettings, it is automatically set by the dyndns module."
              else
                opt.extraSettings;

            service_config = {
              settings = builtins.catAttrs "value" (
                builtins.attrValues (
                  lib.mapAttrs (_: opt: {
                    value =
                      (extraSettingsSafe opt)
                      // {
                        domain = opt.domain;
                        provider = opt.provider;
                      }
                      // {
                        "${opt.secret_field_name}" = secret_id opt;
                      };
                  }) cfg.settings
                )
              );
            };

            secret_generator = _: opt: {
              name = secret_id opt;
              value = {
                share = true;
                prompts.${secret_id opt} = {
                  type = "hidden";
                  persist = true;
                };
              };
            };
          in
          {
            imports = lib.optional cfg.server.enable (
              lib.modules.importApply ./nginx.nix {
                inherit config;
                inherit settings;
                inherit lib;
              }
            );

            clan.core.vars.generators = lib.mkIf (cfg.settings != { }) (
              lib.mapAttrs' secret_generator cfg.settings
            );

            users.groups.${name} = lib.mkIf (cfg.settings != { }) { };
            users.users.${name} = lib.mkIf (cfg.settings != { }) {
              group = name;
              isSystemUser = true;
              description = "User for ${name} service";
              home = "/var/lib/${name}";
              createHome = true;
            };

            services.nginx = lib.mkIf cfg.server.enable {
              virtualHosts = {
                "${cfg.server.domain}" = {
                  forceSSL = true;
                  enableACME = true;
                  locations."/" = {
                    proxyPass = "http://localhost:${toString cfg.server.port}";
                  };
                };
              };
            };

            systemd.services.${name} = lib.mkIf (cfg.settings != { }) {
              path = [ ];
              description = "Dynamic DNS updater";
              after = [ "network.target" ];
              wantedBy = [ "multi-user.target" ];
              environment = {
                MYCONFIG = "${builtins.toJSON service_config}";
                SERVER_ENABLED = if cfg.server.enable then "yes" else "no";
                PERIOD = "${toString cfg.period}m";
                LISTENING_ADDRESS = ":${toString cfg.server.port}";
                GODEBUG = "netdns=go"; # We need to set this untill this has been merged. https://github.com/NixOS/nixpkgs/pull/432758
              };

              serviceConfig =
                let
                  pyscript =
                    pkgs.writers.writePython3Bin "generate_secret_config.py"
                      {
                        libraries = [ ];
                        doCheck = false;
                      }
                      ''
                        import json
                        from pathlib import Path
                        import os

                        cred_dir = Path(os.getenv("CREDENTIALS_DIRECTORY"))
                        config_str = os.getenv("MYCONFIG")


                        def get_credential(name):
                            secret_p = cred_dir / name
                            with open(secret_p, 'r') as f:
                                return f.read().strip()


                        config = json.loads(config_str)
                        print(f"Config: {config}")
                        for attrset in config["settings"]:
                            if "password" in attrset:
                                attrset['password'] = get_credential(attrset['password'])
                            elif "token" in attrset:
                                attrset['token'] = get_credential(attrset['token'])
                            elif "secret_api_key" in attrset:
                                attrset['secret_api_key'] = get_credential(attrset['secret_api_key'])
                            elif "api_key" in attrset:
                                attrset['api_key'] = get_credential(attrset['api_key'])
                            else:
                                raise ValueError(f"Missing secret field in {attrset}")

                        # create directory data if it does not exist
                        data_dir = Path('data')
                        data_dir.mkdir(mode=0o770, exist_ok=True)

                        # Create a temporary config file
                        # with appropriate permissions
                        tmp_config_path = data_dir / '.config.json'
                        tmp_config_path.touch(mode=0o660, exist_ok=False)

                        # Write the config with secrets back
                        with open(tmp_config_path, 'w') as f:
                            f.write(json.dumps(config, indent=4))

                        # Move config into place
                        config_path = data_dir / 'config.json'
                        tmp_config_path.rename(config_path)

                        # Set file permissions to read
                        # and write only by the user and group
                        for file in data_dir.iterdir():
                            file.chmod(0o660)
                      '';
                in
                {
                  ExecStartPre = lib.getExe pyscript;
                  ExecStart = lib.getExe pkgs.ddns-updater;
                  LoadCredential = lib.mapAttrsToList (_: opt: "${secret_id opt}:${secret_path opt}") cfg.settings;
                  User = name;
                  Group = name;
                  NoNewPrivileges = true;
                  PrivateTmp = true;
                  ProtectSystem = "strict";
                  ReadOnlyPaths = "/";
                  PrivateDevices = "yes";
                  ProtectKernelModules = "yes";
                  ProtectKernelTunables = "yes";
                  WorkingDirectory = "/var/lib/${name}";
                  ReadWritePaths = [
                    "/proc/self"
                    "/var/lib/${name}"
                  ];

                  Restart = "always";
                  RestartSec = 60;
                };
            };
          };
      };
  };
}
