{
  _class = "clan.service";
  manifest = {
    name = "monitoring";
    description = "Monitoring stack gathering metrics and logs with a small resource footprint.";
  };

  roles = {
    client = {
      description = "Monitoring clients send their metrics and logs to the monitoring server.";
    };

    server = {
      description = "The monitoring server that stores metrics and logs. Provides optional dashboards and alerting.";

      perInstance =
        { settings, ... }:
        {
          nixosModule =
            { pkgs, config, ... }:
            let
              networkingInterfaces = builtins.attrNames config.networking.interfaces;
            in
            {
              clan.core = {
                state.monitoring.folders = [
                  "/var/lib/mimir"
                ];
              };

              services.nginx = {
                enable = true;
                virtualHosts."${config.networking.fqdn}" = {
                  enableACME = true;
                  forceSSL = true;

                  locations."/mimir/" = {
                    basicAuthFile = config.clan.core.vars.generators.mimir-auth.files.htpasswd.path;
                    proxyPass = "http://127.0.0.1:${builtins.toString config.services.mimir.configuration.server.http_listen_port}${config.services.mimir.configuration.server.http_path_prefix}/";
                  };
                };
              };

              services.mimir = {
                enable = true;
                configuration = {
                  server = {
                    http_listen_port = 3001;
                    http_path_prefix = "/mimir";
                  };
                  usage_stats.enabled = false;
                  multitenancy_enabled = false;

                  alertmanager.sharding_ring = {
                    replication_factor = 1;
                    instance_interface_names = networkingInterfaces;
                  };

                  api.prometheus_http_prefix = "/prometheus";

                  compactor.sharding_ring.instance_interface_names = networkingInterfaces;

                  distributor.ring = {
                    instance_interface_names = networkingInterfaces;
                    instance_addr = "127.0.0.1";
                  };

                  frontend.instance_interface_names = networkingInterfaces;

                  ingester.ring = {
                    instance_addr = "127.0.0.1";
                    replication_factor = 1;
                    instance_interface_names = networkingInterfaces;
                  };

                  memberlist.bind_addr = [ "127.0.0.1" ];

                  query_scheduler.ring.instance_interface_names = networkingInterfaces;

                  ruler.ring.instance_interface_names = networkingInterfaces;

                  store_gateway.sharding_ring = {
                    replication_factor = 1;
                    instance_interface_names = networkingInterfaces;
                  };
                };
              };
            };
        };
    };
  };

  perMachine.nixosModule =
    { pkgs, ... }:
    {
      clan.core.vars.generators = {
        mimir-auth = {
          share = true;

          files."username" = {
            secret = false;
          };
          files."password" = {
            owner = "alloy";
            secret = true;
          };
          files."htpasswd" = {
            secret = true;
            owner = "nginx";
          };

          runtimeInputs = [
            pkgs.openssl
            pkgs.apacheHttpd
          ];
          script = ''
            echo -n "alloy" > $out/username
            openssl rand -hex 32 > $out/password
            htpasswd -nbB "$(cat $out/username)" "$(cat $out/password)" > $out/htpasswd
          '';
        };
      };
    };
}
