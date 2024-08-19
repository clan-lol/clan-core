{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.clan.vaultwarden;
  module_name = "vaultwarden";

  admin_pwd_secret = "${module_name}-admin";
  admin_pwd_hash_secret = "${admin_pwd_secret}-hash";
  smtp_pwd_secret = "${module_name}-smtp";
  smtp_pwd_secret_path =
    config.clan.core.facts.services."${smtp_pwd_secret}".secret."${smtp_pwd_secret}".path;
  admin_secret_cfg_path =
    config.clan.core.facts.services."${admin_pwd_secret}".secret."${admin_pwd_hash_secret}".path;
in

{
  imports = [
    ../postgresql
    (lib.mkRemovedOptionModule [
      "clan"
      "vaultwarden"
      "enable"
    ] "Importing the module will already enable the service.")
    ../nginx
  ];

  options.clan."${module_name}" = {
    domain = lib.mkOption {
      type = lib.types.str;
      example = "bitwarden.example.com";
      description = "The domain to use for Vaultwarden";
    };
    port = lib.mkOption {
      type = lib.types.int;
      default = 3011;
      description = "The port to use for Vaultwarden";
    };
    allow_signups = lib.mkOption {
      type = lib.types.bool;
      default = false;
      description = "Allow signups for new users";
    };

    smtp = {
      host = lib.mkOption {
        type = lib.types.str;
        example = "smtp.example.com";
        description = "The email server domain address";
      };
      from = lib.mkOption {
        type = lib.types.str;
        example = "foobar@example.com";
        description = "From whom the email is coming from";
      };
      username = lib.mkOption {
        type = lib.types.str;
        example = "foobar@example.com";
        description = "The email server username";
      };
    };
  };

  config = {

    clan.postgresql.users.vaultwarden = { };
    clan.postgresql.databases.vaultwarden.create.options = {
      TEMPLATE = "template0";
      LC_COLLATE = "C";
      LC_CTYPE = "C";
      ENCODING = "UTF8";
      OWNER = "vaultwarden";
    };
    clan.postgresql.databases.vaultwarden.restore.stopOnRestore = [ "vaultwarden" ];

    services.nginx = {
      enable = true;
      virtualHosts = {
        "${cfg.domain}" = {
          forceSSL = true;
          enableACME = true;
          extraConfig = ''
            client_max_body_size 128M;
          '';
          locations."/" = {
            proxyPass = "http://localhost:${builtins.toString cfg.port}";
            proxyWebsockets = true;
          };
          locations."/notifications/hub" = {
            proxyPass = "http://localhost:${builtins.toString cfg.port}";
            proxyWebsockets = true;
          };
          locations."/notifications/hub/negotiate" = {
            proxyPass = "http://localhost:${builtins.toString cfg.port}";
            proxyWebsockets = true;
          };
        };
      };
    };

    clan.core.facts.services = {
      "${admin_pwd_secret}" = {
        secret."${admin_pwd_secret}" = { };
        secret."${admin_pwd_hash_secret}" = { };
        generator.path = with pkgs; [
          coreutils
          pwgen
          libargon2
          openssl
        ];
        generator.script = ''
          ADMIN_PWD=$(pwgen 16 -n1 | tr -d "\n")
          ADMIN_HASH=$(echo -n "$ADMIN_PWD" | argon2 "$(openssl rand -base64 32)" -e -id -k 65540 -t 3 -p 4)

          config="
          ADMIN_TOKEN=\"$ADMIN_HASH\"
          "
          echo -n "$ADMIN_PWD" > $secrets/${admin_pwd_secret}
          echo -n "$config" > $secrets/${admin_pwd_hash_secret}
        '';
      };
      "${smtp_pwd_secret}" = {
        secret."${smtp_pwd_secret}" = { };
        generator.prompt = "${cfg.smtp.from} SMTP password";
        generator.path = with pkgs; [ coreutils ];
        generator.script = ''
          config="
            SMTP_PASSWORD="$prompt_value"
          "
          echo -n "$config" > $secrets/${smtp_pwd_secret}
        '';
      };
    };

    systemd.services."${module_name}" = {
      serviceConfig = {
        EnvironmentFile = [ smtp_pwd_secret_path ];
      };
    };

    services."${module_name}" = {
      enable = true;
      dbBackend = "postgresql";
      environmentFile = admin_secret_cfg_path; # TODO: Make this upstream an array
      config = {
        SMTP_SECURITY = "force_tls";
        SMTP_HOST = cfg.smtp.host;
        SMTP_FROM = cfg.smtp.from;
        SMTP_USERNAME = cfg.smtp.username;
        DOMAIN = "https://${cfg.domain}";
        SIGNUPS_ALLOWED = cfg.allow_signups;
        ROCKET_PORT = builtins.toString cfg.port;
        DATABASE_URL = "postgresql://"; # TODO: This should be set upstream if dbBackend is set to postgresql
        ENABLE_WEBSOCKET = true;
        ROCKET_ADDRESS = "127.0.0.1";
      };
    };

  };

}
