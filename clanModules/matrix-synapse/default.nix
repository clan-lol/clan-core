{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.clan.matrix-synapse;
in
{
  options.clan.matrix-synapse = {
    enable = lib.mkEnableOption "Enable matrix-synapse";
    domain = lib.mkOption {
      type = lib.types.str;
      description = "The domain name of the matrix server";
    };
  };
  config = lib.mkIf cfg.enable {
    services.matrix-synapse = {
      enable = true;
      settings = {
        server_name = cfg.domain;
        database = {
          args.user = "matrix-synapse";
          args.database = "matrix-synapse";
          name = "psycopg2";
        };
        turn_uris = [
          "turn:turn.matrix.org?transport=udp"
          "turn:turn.matrix.org?transport=tcp"
        ];
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
      extraConfigFiles = [ "/var/lib/matrix-synapse/registration_shared_secret.yaml" ];
    };
    systemd.services.matrix-synapse.serviceConfig.ExecStartPre = [
      "+${pkgs.writeScript "copy_registration_shared_secret" ''
        #!/bin/sh
        cp ${config.clanCore.facts.services.matrix-synapse.secret.synapse-registration_shared_secret.path} /var/lib/matrix-synapse/registration_shared_secret.yaml
        chown matrix-synapse:matrix-synapse /var/lib/matrix-synapse/registration_shared_secret.yaml
        chmod 600 /var/lib/matrix-synapse/registration_shared_secret.yaml
      ''}"
    ];

    clanCore.facts.services."matrix-synapse" = {
      secret."synapse-registration_shared_secret" = { };
      generator.path = with pkgs; [
        coreutils
        pwgen
      ];
      generator.script = ''
        echo "registration_shared_secret: $(pwgen -s 32 1)" > "$secrets"/synapse-registration_shared_secret
      '';
    };

    services.postgresql.enable = true;
    # we need to use both ensusureDatabases and initialScript, because the former runs everytime but with the wrong collation
    services.postgresql = {
      ensureDatabases = [ "matrix-synapse" ];
      ensureUsers = [
        {
          name = "matrix-synapse";
          ensureDBOwnership = true;
        }
      ];
      initialScript = pkgs.writeText "synapse-init.sql" ''
        CREATE DATABASE "matrix-synapse"
          TEMPLATE template0
          LC_COLLATE = "C"
          LC_CTYPE = "C";
      '';
    };
    services.nginx = {
      enable = true;
      virtualHosts = {
        ${cfg.domain} = {
          locations."= /.well-known/matrix/server".extraConfig = ''
            add_header Content-Type application/json;
            return 200 '${builtins.toJSON { "m.server" = "matrix.${cfg.domain}:443"; }}';
          '';
          locations."= /.well-known/matrix/client".extraConfig = ''
            add_header Content-Type application/json;
            add_header Access-Control-Allow-Origin *;
            return 200 '${
              builtins.toJSON {
                "m.homeserver" = {
                  "base_url" = "https://matrix.${cfg.domain}";
                };
                "m.identity_server" = {
                  "base_url" = "https://vector.im";
                };
              }
            }';
          '';
        };
        "matrix.${cfg.domain}" = {
          forceSSL = true;
          enableACME = true;
          locations."/_matrix" = {
            proxyPass = "http://localhost:8008";
          };
          locations."/test".extraConfig = ''
            return 200 "Hello, world!";
          '';
        };
      };
    };
  };
}
