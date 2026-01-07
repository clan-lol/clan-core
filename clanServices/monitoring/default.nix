{
  _class = "clan.service";
  manifest = {
    name = "monitoring";
    description = "Monitoring stack gathering metrics and logs with a small resource footprint.";
    readme = builtins.readFile ./README.md;
  };

  roles = {
    client = {
      description = "Monitoring clients send their metrics and logs to the monitoring server.";

      interface =
        { lib, ... }:
        {
          options = {
            monitoredSystemdServices = lib.mkOption {
              type = lib.types.either (lib.types.enum [
                "all"
                "nixos"
              ]) (lib.types.listOf lib.types.str);
              default = "nixos";
              description = ''
                List of systemd services which are shown in the clan infrastructure grafana dashboard.
                Logs sent to the monitoring server are filtered using this list.

                Options:
                "all" - all systemd services
                "nixos" (default) - services that have been explicitly enabled through nixos config
                listOf str - custom list of systemd services
              '';
              example = [
                "alloy.service"
                "grafana.service"
                "loki.service"
                "mimir.service"
                "nginx.service"
              ];
            };
          };
        };

      perInstance =
        { roles, settings, ... }:
        {
          nixosModule =
            {
              config,
              lib,
              options,
              ...
            }:
            {
              services.alloy =
                let
                  serverAddress = lib.head (
                    map (m: "http://${m}.${config.clan.core.settings.domain}") (lib.attrNames roles.server.machines)
                  );

                  enabledNixosSystemdServices = builtins.map (v: "${v}.service") (
                    lib.attrNames (
                      lib.attrsets.filterAttrs (_name: value: value == true) (
                        lib.mapAttrs (
                          name: value:
                          builtins.hasAttr "enable" options.services."${name}"
                          && builtins.hasAttr "default" options.services."${name}".enable
                          && options.services."${name}".enable.default != value.enable
                          && value.enable == true
                        ) (config.services)
                      )
                    )
                  );

                  monitoredServices = (
                    if settings.monitoredSystemdServices == "nixos" then
                      enabledNixosSystemdServices
                    else
                      settings.monitoredSystemdServices
                  );
                in
                {
                  enable = true;
                  extraFlags = [
                    "--server.http.enable-pprof=false"
                    "--disable-reporting=true"
                  ];
                  configPath = builtins.toFile "config.alloy" ''
                    // Collects metrics and sends them to mimir.
                    prometheus.exporter.unix "local_system" {
                      // See the list of available collectors in the alloy docs at
                      // https://grafana.com/docs/alloy/latest/reference/components/prometheus/prometheus.exporter.unix/#collectors-list
                      set_collectors = [ "cpu", "filesystem", "meminfo", "systemd" ]
                    }

                    prometheus.scrape "scrape_metrics" {
                      targets = prometheus.exporter.unix.local_system.targets
                      forward_to = [prometheus.relabel.create_nixos_services_metric.receiver, prometheus.remote_write.mimir.receiver]
                      scrape_interval = "10s"
                    }

                    prometheus.relabel "create_nixos_services_metric" {
                      forward_to = [prometheus.remote_write.mimir.receiver]

                      ${
                        if settings.monitoredSystemdServices == "all" then
                          ''
                            rule {
                              action = "keep"
                              source_labels = ["__name__"]
                              regex = "node_systemd_unit_state"
                            }
                          ''
                        else
                          ''
                            rule {
                              action = "keep"
                              source_labels = ["__name__", "name"]
                              regex = "node_systemd_unit_state;(${lib.strings.join "|" monitoredServices})"
                            }
                          ''
                      }

                      rule {
                        action = "replace"
                        target_label = "__name__"
                        replacement = "nixos_systemd_unit_state"
                      }
                    }

                    prometheus.remote_write "mimir" {
                      endpoint {
                        url = "${serverAddress}/mimir/api/v1/push"
                        basic_auth {
                          username = "${config.clan.core.vars.generators.mimir-auth.files.username.value}"
                          password_file = "${config.clan.core.vars.generators.mimir-auth.files.password.path}"
                        }
                      }
                    }

                    // Collects logs and sends them to loki.
                    ${
                      if settings.monitoredSystemdServices == "all" then
                        ''
                          loki.source.journal "all" {
                            relabel_rules = loki.relabel.journal.rules
                            forward_to = [loki.write.loki.receiver]
                          }
                        ''
                      else
                        lib.concatStrings (
                          builtins.map (monitoredService: ''
                            loki.source.journal "${builtins.replaceStrings [ "-" "." ] [ "_" "_" ] monitoredService}" {
                              matches = "_SYSTEMD_UNIT=${monitoredService}"
                              relabel_rules = loki.relabel.journal.rules
                              forward_to = [loki.write.loki.receiver]
                            }
                          '') monitoredServices
                        )
                    }

                    loki.relabel "journal" {
                      rule {
                        source_labels = ["__journal__hostname"]
                        target_label = "instance"
                      }
                      rule {
                        source_labels = ["__journal__systemd_unit"]
                        target_label = "service_name"
                      }
                      rule {
                        source_labels = ["__journal_priority_keyword"]
                        target_label = "level"
                      }
                      forward_to = []
                    }

                    loki.write "loki" {
                      endpoint {
                        url = "${serverAddress}/loki/loki/api/v1/push"
                        basic_auth {
                          username = "${config.clan.core.vars.generators.loki-auth.files.username.value}"
                          password_file = "${config.clan.core.vars.generators.loki-auth.files.password.path}"
                        }
                      }
                    }
                  '';
                };
            };
        };
    };

    server = {
      description = "The monitoring server that stores metrics and logs. Provides optional dashboards and alerting.";

      interface =
        { lib, ... }:
        {
          options.grafana.enable = lib.mkEnableOption "grafana";
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
            let
              networkingInterfaces = builtins.attrNames config.networking.interfaces;
              defaultVirtualHost = config.services.nginx.virtualHosts."${config.networking.fqdn}";
              useSSL = defaultVirtualHost.addSSL || defaultVirtualHost.forceSSL || defaultVirtualHost.onlySSL;
            in
            {
              networking.firewall.allowedTCPPorts = [ 80 ] ++ lib.lists.optional useSSL 443;

              clan.core = {
                postgresql = {
                  enable = true;
                  users.grafana = { };
                  databases.grafana = {
                    create.options = {
                      OWNER = "grafana";
                    };
                    restore.stopOnRestore = [ "grafana" ];
                  };
                };

                state.monitoring.folders = [
                  "/var/lib/mimir"
                  config.services.loki.dataDir
                ];

                vars.generators.grafana-admin = {
                  prompts = {
                    username = {
                      description = "Username of the grafana admin user";
                    };
                  };

                  files = {
                    username = {
                      secret = false;
                    };
                    password = {
                      owner = "grafana";
                      secret = true;
                    };
                  };

                  runtimeInputs = [
                    pkgs.openssl
                  ];
                  script = ''
                    cat "$prompts/username" > $out/username
                    openssl rand -hex 32 > $out/password
                  '';
                };
              };

              services.nginx = {
                enable = true;
                virtualHosts."${config.networking.fqdn}" = {
                  locations."/mimir/" = {
                    basicAuthFile = config.clan.core.vars.generators.mimir-auth.files.htpasswd.path;
                    proxyPass = "http://127.0.0.1:${builtins.toString config.services.mimir.configuration.server.http_listen_port}${config.services.mimir.configuration.server.http_path_prefix}/";
                  };

                  locations."/loki/" = {
                    basicAuthFile = config.clan.core.vars.generators.loki-auth.files.htpasswd.path;
                    proxyPass = "http://127.0.0.1:${builtins.toString config.services.loki.configuration.server.http_listen_port}${config.services.loki.configuration.server.http_path_prefix}/";
                  };

                  locations."/" = {
                    proxyPass = "http://127.0.0.1:${builtins.toString config.services.grafana.settings.server.http_port}/";
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

              services.grafana = {
                enable = settings.grafana.enable;
                settings = {
                  analytics = {
                    enabled = false;
                    reporting_enabled = false;
                    check_for_updates = false;
                    check_for_plugin_updates = false;
                    feedback_links_enabled = false;
                  };

                  database = {
                    type = "postgres";
                    host = "/run/postgresql";
                    user = "grafana";
                    name = "grafana";
                  };

                  metrics.enabled = false;
                  public_dashboards.enabled = false;

                  security = {
                    admin_user = "$__file{${config.clan.core.vars.generators.grafana-admin.files.username.path}}";
                    admin_password = "$__file{${config.clan.core.vars.generators.grafana-admin.files.password.path}}";
                    cookie_secure = true;
                  };

                  server = {
                    domain = config.networking.fqdn;
                    root_url = "http" + lib.optionalString useSSL "s" + "://${config.networking.fqdn}/";
                  };

                  snapshots = {
                    enabled = false;
                    external_enabled = false;
                  };
                };

                provision = {
                  enable = true;

                  dashboards.settings.providers = [
                    {
                      name = "clan";
                      options.path = ./dashboards;
                    }
                  ];

                  datasources.settings.datasources = [
                    {
                      name = "mimir";
                      url = "http://127.0.0.1:${builtins.toString config.services.mimir.configuration.server.http_listen_port}${config.services.mimir.configuration.server.http_path_prefix}${config.services.mimir.configuration.api.prometheus_http_prefix}";
                      type = "prometheus";
                      isDefault = true;
                      jsonData.manageAlerts = false;
                    }
                    {
                      name = "loki";
                      url = "http://127.0.0.1:${builtins.toString config.services.loki.configuration.server.http_listen_port}${config.services.loki.configuration.server.http_path_prefix}";
                      type = "loki";
                      jsonData.manageAlerts = false;
                    }
                  ];
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
