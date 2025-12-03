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
                  config.services.loki.dataDir
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

                  locations."/loki/" = {
                    basicAuthFile = config.clan.core.vars.generators.loki-auth.files.htpasswd.path;
                    proxyPass = "http://127.0.0.1:${builtins.toString config.services.loki.configuration.server.http_listen_port}${config.services.loki.configuration.server.http_path_prefix}/";
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

              services.loki = {
                enable = true;

                configuration = {
                  analytics.reporting_enabled = false;

                  auth_enabled = false;

                  common = {
                    path_prefix = config.services.loki.dataDir;
                    replication_factor = 1;
                    instance_interface_names = networkingInterfaces;
                    ring = {
                      instance_addr = "127.0.0.1";
                      kvstore.store = "inmemory";
                    };
                  };

                  schema_config = {
                    configs = [
                      {
                        from = "2025-11-01";
                        object_store = "filesystem";
                        schema = "v13";
                        store = "tsdb";
                        index = {
                          prefix = "index_";
                          period = "24h";
                        };
                      }
                    ];
                  };

                  server = {
                    http_listen_port = 3002;
                    http_path_prefix = "/loki";
                    grpc_listen_port = 9096;
                  };

                  storage_config.filesystem.directory = "${config.services.loki.dataDir}/chunks";
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
        loki-auth = {
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
