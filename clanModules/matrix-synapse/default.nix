{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.clan.matrix-synapse;
  nginx-vhost = "matrix.${config.clan.matrix-synapse.domain}";
  element-web =
    pkgs.runCommand "element-web-with-config" { nativeBuildInputs = [ pkgs.buildPackages.jq ]; } ''
      cp -r ${pkgs.element-web} $out
      chmod -R u+w $out
      jq '."default_server_config"."m.homeserver" = { "base_url": "https://${nginx-vhost}:443", "server_name": "${config.clan.matrix-synapse.domain}" }' \
        > $out/config.json < ${pkgs.element-web}/config.json
      ln -s $out/config.json $out/config.${nginx-vhost}.json
    '';
in
{
  options.clan.matrix-synapse = {
    enable = lib.mkEnableOption "Enable matrix-synapse";
    domain = lib.mkOption {
      type = lib.types.str;
      description = "The domain name of the matrix server";
      example = "example.com";
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
      extraConfigFiles = [ "/run/synapse-registration-shared-secret.yaml" ];
    };
    systemd.tmpfiles.settings."synapse" = {
      "/run/synapse-registration-shared-secret.yaml" = {
        C.argument = config.clanCore.facts.services.matrix-synapse.secret.synapse-registration_shared_secret.path;
        z = {
          mode = "0400";
          user = "matrix-synapse";
        };
      };
    };

    systemd.services.matrix-synapse.serviceConfig.ExecStartPre = [
      "+${pkgs.writeShellScript "create-matrix-synapse-db" ''
        export PATH=${
          lib.makeBinPath [
            config.services.postgresql.package
            pkgs.util-linux
            pkgs.gnugrep
          ]
        }
        psql() { runuser -u postgres -- psql "$@"; }
        # wait for postgres to be ready
        while ! runuser -u postgres pg_isready; do
          sleep 1
        done
        if ! psql -tAc "SELECT 1 FROM pg_database WHERE datname = 'matrix-synapse'" | grep -q 1; then
          psql -c "CREATE DATABASE \"matrix-synapse\" TEMPLATE template0 LC_COLLATE = 'C' LC_CTYPE = 'C'"
        fi
        # create user if it doesn't exist and make it owner of the database
        if ! psql -tAc "SELECT 1 FROM pg_user WHERE usename = 'matrix-synapse'" | grep -q 1; then
          psql -c "CREATE USER \"matrix-synapse\""
          psql -c "ALTER DATABASE \"matrix-synapse\" OWNER TO \"matrix-synapse\""
        fi
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
                  "base_url" = "https://${nginx-vhost}";
                };
                "m.identity_server" = {
                  "base_url" = "https://vector.im";
                };
              }
            }';
          '';
        };
        ${nginx-vhost} = {
          forceSSL = true;
          enableACME = true;
          locations."/_matrix".proxyPass = "http://localhost:8008";
          locations."/_synapse".proxyPass = "http://localhost:8008";
          locations."/".root = element-web;
        };
      };
    };
  };
}
