{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/matrix-synapese";
  manifest.description = "A federated messaging server with end-to-end encryption.";
  manifest.categories = [ "Social" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.default = {
    description = "Placeholder role to apply the matrix-synapse service";
    interface =
      { lib, ... }:
      {
        options = {

          acmeEmail = lib.mkOption {
            type = lib.types.str;
            description = ''
              Email address for account creation and correspondence from the CA.
              It is recommended to use the same email for all certs to avoid account
              creation limits.
            '';
          };

          services.matrix-synapse.package = lib.mkOption {
            readOnly = false;
            description = "Package to use for matrix-synapse";
          };

          server_tld = lib.mkOption {
            type = lib.types.str;
            description = "The address that is suffixed after your username i.e @alice:example.com";
            example = "example.com";
          };

          app_domain = lib.mkOption {
            type = lib.types.str;
            description = "The matrix server hostname also serves the element client";
            example = "matrix.example.com";
          };

          users = lib.mkOption {
            default = { };
            type = lib.types.attrsOf (
              lib.types.submodule (
                { name, ... }:
                {
                  options = {
                    name = lib.mkOption {
                      type = lib.types.str;
                      default = name;
                      description = "The name of the user";
                    };

                    admin = lib.mkOption {
                      type = lib.types.bool;
                      default = false;
                      description = "Whether the user should be an admin";
                    };
                  };
                }
              )
            );
            description = "A list of users. Not that only new users will be created and existing ones are not modified.";
            example.alice = {
              admin = true;
            };
          };
        };
      };

    perInstance =
      { settings, ... }:
      {
        nixosModule =
          {
            pkgs,
            config,
            lib,
            ...
          }:
          {

            imports = [ ./nginx.nix ];

            security.acme.defaults.email = settings.acmeEmail;

            services.matrix-synapse = {
              enable = true;
              settings = {
                server_name = settings.server_tld;
                database = {
                  args.user = "matrix-synapse";
                  args.database = "matrix-synapse";
                  name = "psycopg2";
                };
                turn_uris = [
                  "turn:turn.matrix.org?transport=udp"
                  "turn:turn.matrix.org?transport=tcp"
                ];
                registration_shared_secret_path = "/run/synapse-registration-shared-secret";
                listeners = [
                  {
                    port = 8008;
                    bind_addresses = [ "::1" ];
                    type = "http";
                    tls = false;
                    x_forwarded = true;
                    resources = [
                      {
                        names = [ "client" ];
                        compress = true;
                      }
                      {
                        names = [ "federation" ];
                        compress = false;
                      }
                    ];
                  }
                ];
              };
            };

            clan.core.postgresql.enable = true;
            clan.core.postgresql.users.matrix-synapse = { };
            clan.core.postgresql.databases.matrix-synapse.create.options = {
              TEMPLATE = "template0";
              LC_COLLATE = "C";
              LC_CTYPE = "C";
              ENCODING = "UTF8";
              OWNER = "matrix-synapse";
            };
            clan.core.postgresql.databases.matrix-synapse.restore.stopOnRestore = [ "matrix-synapse" ];

            clan.core.vars.generators = {
              "matrix-synapse" = {
                files."synapse-registration_shared_secret" = { };
                runtimeInputs = with pkgs; [
                  coreutils
                  pwgen
                ];
                script = ''
                  echo -n "$(pwgen -s 32 1)" > "$out"/synapse-registration_shared_secret
                '';
              };
            }
            // lib.mapAttrs' (
              _name: user:
              lib.nameValuePair "matrix-password-${user.name}" {
                files."matrix-password-${user.name}" = { };
                runtimeInputs = with pkgs; [ xkcdpass ];
                script = ''
                  xkcdpass -n 4 -d - > "$out"/${lib.escapeShellArg "matrix-password-${user.name}"}
                '';
              }
            ) settings.users;

            systemd.services.matrix-synapse =
              let
                usersScript = ''
                  while ! ${pkgs.netcat}/bin/nc -z -v ::1 8008; do
                    if ! kill -0 "$MAINPID"; then exit 1; fi
                    sleep 1;
                  done
                ''
                + lib.concatMapStringsSep "\n" (user: ''
                  # only create user if it doesn't exist
                  /run/current-system/sw/bin/matrix-synapse-register_new_matrix_user --exists-ok --password-file ${
                    config.clan.core.vars.generators."matrix-password-${user.name}".files."matrix-password-${user.name}".path
                  } --user "${user.name}" ${if user.admin then "--admin" else "--no-admin"}
                '') (lib.attrValues settings.users);
              in
              {
                path = [ pkgs.curl ];
                serviceConfig.ExecStartPre = lib.mkBefore [
                  "+${pkgs.coreutils}/bin/install -o matrix-synapse -g matrix-synapse ${
                    lib.escapeShellArg
                      config.clan.core.vars.generators.matrix-synapse.files."synapse-registration_shared_secret".path
                  } /run/synapse-registration-shared-secret"
                ];
                serviceConfig.ExecStartPost = [
                  ''+${pkgs.writeShellScript "matrix-synapse-create-users" usersScript}''
                ];
              };

            services.nginx = {
              enable = true;
              virtualHosts = {
                "${settings.server_tld}" = {
                  locations."= /.well-known/matrix/server".extraConfig = ''
                    add_header Content-Type application/json;
                    return 200 '${builtins.toJSON { "m.server" = "${settings.app_domain}:443"; }}';
                  '';
                  locations."= /.well-known/matrix/client".extraConfig = ''
                    add_header Content-Type application/json;
                    add_header Access-Control-Allow-Origin *;
                    return 200 '${
                      builtins.toJSON {
                        "m.homeserver" = {
                          "base_url" = "https://${settings.app_domain}";
                        };
                        "m.identity_server" = {
                          "base_url" = "https://vector.im";
                        };
                      }
                    }';
                  '';
                  forceSSL = true;
                  enableACME = true;
                };
                "${settings.app_domain}" =
                  let
                    # FIXME: This was taken from upstream. Drop this when our patch is upstream
                    element-web =
                      pkgs.runCommand "element-web-with-config" { nativeBuildInputs = [ pkgs.buildPackages.jq ]; }
                        ''
                          cp -r ${pkgs.element-web} $out
                          chmod -R u+w $out
                          jq '."default_server_config"."m.homeserver" = { "base_url": "https://${settings.app_domain}:443", "server_name": "${settings.server_tld}" }' \
                            > $out/config.json < ${pkgs.element-web}/config.json
                          ln -s $out/config.json $out/config.${settings.app_domain}.json
                        '';
                  in
                  {
                    forceSSL = true;
                    enableACME = true;
                    locations."/".root = element-web;
                    locations."/_matrix".proxyPass = "http://localhost:8008"; # TODO: We should make the port configurable
                    locations."/_synapse".proxyPass = "http://localhost:8008";
                  };
              };
            };
          };
      };
  };
}
