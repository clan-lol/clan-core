{
  pkgs,
  config,
  ...
}:
{

   # services.nginx.virtualHosts."cloud.local".listen = [{ addr = "127.0.0.1"; port = 8009; }];


   services = {
    nginx.virtualHosts = {
      "cloud.local" = {
        # forceSSL = true;
        # enableACME = true;
      #  locations = {
      #   "cloud.clan" = {
      #     # proxyPass = "http://[::1]:6167";
      #     proxyPass = "http://127.0.0.1/8009";
      #     extraConfig = ''
      #       proxy_set_header Host $host;
      #       proxy_buffering off;
      #     '';
      #   };
      # };

      };

      "onlyoffice.example.com" = {
        # forceSSL = true;
        # enableACME = true;
      };
    };
  };

  services.nextcloud = {
    enable = true;
    hostName = "cloud.local";
    package = pkgs.nextcloud28;
    database.createLocally = true;
    # datadir = "/var/lib/nextcloud/data";
    home = "/var/lib/nextcloud";
    config = {
      adminpassFile = "/var/lib/nextcloud/adminPassword";
      dbtype = "pgsql";
      dbname = "nextcloud";
      trustedProxies = [ "localhost" "127.0.0.1" ];
      # extraTrustedDomains = [ "cloud.local" ];
    };
    settings = {
      "trusted_domains" = [ "cloud.local" ];
    };
  };

  systemd.tmpfiles.rules = [
    # "d '/var/lib/nextcloud' 0770 'nextcloud' 'nextcloud' - -"
    # "d '/var/lib/nextcloud/data' 0770 'nextcloud' 'nextcloud' - -"
    "C '/var/lib/nextcloud/adminPassword' 0644 'nextcloud' 'nextcloud' - ${
      config.clanCore.facts.services.nextcloud.secret.adminPassword.path or ""
    }"
    "C '/var/lib/nextcloud/databasePassword' 0644 'nextcloud' 'nextcloud' - ${
      config.clanCore.facts.services.nextcloud.secret.databasePassword.path or ""
    }"
  ];

  clanCore.state.nextcloud.folders = [ "/var/lib/nextcloud" ];

  clanCore.facts.services.nextcloud = {
    secret."adminPassword" = { };
    secret."databasePassword" = { };
    generator.prompt = ''
    Please set your nextcloud administration password:
    '';
    generator.path = [
      pkgs.coreutils
    ];
    generator.script = ''
      echo $prompt_value > "$secrets"/adminPassword
      echo $prompt_value > "$secrets"/databasePassword
    '';
  };
}
