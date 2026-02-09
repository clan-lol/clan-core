{ clanLib, lib }:
{
  test_simple =
    let
      eval = clanLib.clan {
        # Inject exports from the top-level
        exports."A:::sara".networking.host = lib.mkForce "shitty-gritty";

        directory = ./.;
        self = {
          clan = eval.config;
          inputs = { };
        };

        machines.jon = { };
        machines.sara = { };

        # Override to decouple from implementation state
        exportInterfaces = lib.mkForce {
          networking =
            { ... }:
            {
              options.host = lib.mkOption {
                type = lib.types.str;
              };
            };
          bar =
            { ... }:
            {
              options.opt = lib.mkOption {
                type = lib.types.str;
              };
            };
        };

        ####### Service module "A"
        modules.service-A =
          { ... }:
          {
            manifest.name = "A";
            manifest.exports.out = [
              "networking"
            ];

            roles.default = {
              perInstance =
                {
                  mkExports,
                  ...
                }:
                {
                  exports = mkExports {
                    # Bad but possible for debugging
                    # Circumvents introspection
                    # Should use submodule instead of submoduleWith to use
                    # onlyDefinesConfig
                    imports = [
                      eval.config.exportInterfaces.bar
                    ];

                    networking.host = "foo";
                    bar.opt = "barbar";
                  };
                };
            };

            perMachine =
              { mkExports, ... }:
              {
                exports = mkExports {
                  networking.host = "42";
                };
              };
          };
        ####### Service module "A"
        modules.service-B =
          { exports, ... }:
          {
            manifest.name = "B";
            manifest.exports.out = [ "bar" ];

            roles.default = {
              perInstance =
                {
                  machine,
                  mkExports,
                  ...
                }:
                {
                  exports = mkExports {
                    bar.opt = "foo" + exports."A:::${machine.name}".networking.host;
                    # foo = exports."B:::".foo + exports."A:iA1:default:${machine.name}".foo;
                  };
                };
            };
          };
        #######

        inventory = {
          instances.iA1 = {
            module.name = "service-A";
            module.input = "self";
            roles.default.tags = [ "all" ];
          };
          instances.iA2 = {
            module.name = "service-A";
            module.input = "self";
            roles.default.tags = [ "all" ];
          };
          instances.iB = {
            module.name = "service-B";
            module.input = "self";
            roles.default.tags = [ "all" ];
          };
        };
      };
    in
    {
      inherit eval;
      expr = clanLib.selectExports (_: true) eval.config.exports;
      expected = {
        "A:::jon" = {
          networking = {
            host = "42";
          };
        };
        "A:::sara" = {
          networking = {
            host = "shitty-gritty";
          };
        };
        "A:iA1:default:jon" = {
          bar = {
            opt = "barbar";
          };
          networking = {
            host = "foo";
          };
        };
        "A:iA1:default:sara" = {
          bar = {
            opt = "barbar";
          };
          networking = {
            host = "foo";
          };
        };
        "A:iA2:default:jon" = {
          bar = {
            opt = "barbar";
          };
          networking = {
            host = "foo";
          };
        };
        "A:iA2:default:sara" = {
          bar = {
            opt = "barbar";
          };
          networking = {
            host = "foo";
          };
        };
        "B:iB:default:jon" = {
          bar = {
            opt = "foo42";
          };
        };
        "B:iB:default:sara" = {
          bar = {
            opt = "fooshitty-gritty";
          };
        };
      };
    };

  # Regression test: per-instance exports must not shadow service-level
  # networking values with defaults. When a service sets networking.priority at
  # the service level but only peer data per-instance, the per-instance export
  # must have networking = null (absent), not a default-filled attrset.
  test_unused_interfaces_are_null =
    let
      eval = clanLib.clan {
        directory = ./.;
        self = {
          clan = eval.config;
          inputs = { };
        };

        machines.roci = { };

        modules.my-vpn =
          {
            clanLib,
            config,
            lib,
            ...
          }:
          {
            manifest.name = "my-vpn";
            manifest.exports.out = [
              "networking"
              "peer"
            ];

            # Service-level export: sets networking priority
            exports = lib.mapAttrs' (instanceName: _: {
              name = clanLib.buildScopeKey {
                inherit instanceName;
                serviceName = config.manifest.name;
              };
              value = {
                networking.priority = 900;
                networking.module = "clan_lib.network.direct";
              };
            }) config.instances;

            # Per-instance export: only sets peer data, not networking
            roles.default = {
              perInstance =
                { mkExports, ... }:
                {
                  exports = mkExports {
                    peer.hosts = [
                      { plain = "10.0.0.1"; }
                    ];
                  };
                };
            };
          };

        inventory = {
          instances.vpn1 = {
            module.name = "my-vpn";
            module.input = "self";
            roles.default.machines.roci = { };
          };
        };
      };
    in
    {
      inherit eval;
      # Service-level export has networking with the configured priority
      expr = eval.config.exports."my-vpn:vpn1::".networking;
      expected = {
        priority = 900;
        module = "clan_lib.network.direct";
      };
    };

  test_unused_interfaces_are_null_peer =
    let
      eval = clanLib.clan {
        directory = ./.;
        self = {
          clan = eval.config;
          inputs = { };
        };

        machines.roci = { };

        modules.my-vpn =
          {
            clanLib,
            config,
            lib,
            ...
          }:
          {
            manifest.name = "my-vpn";
            manifest.exports.out = [
              "networking"
              "peer"
            ];

            exports = lib.mapAttrs' (instanceName: _: {
              name = clanLib.buildScopeKey {
                inherit instanceName;
                serviceName = config.manifest.name;
              };
              value = {
                networking.priority = 900;
                networking.module = "clan_lib.network.direct";
              };
            }) config.instances;

            roles.default = {
              perInstance =
                { mkExports, ... }:
                {
                  exports = mkExports {
                    peer.hosts = [
                      { plain = "10.0.0.1"; }
                    ];
                  };
                };
            };
          };

        inventory = {
          instances.vpn1 = {
            module.name = "my-vpn";
            module.input = "self";
            roles.default.machines.roci = { };
          };
        };
      };
    in
    {
      inherit eval;
      # Per-instance export must NOT have networking (it should be null)
      expr = eval.config.exports."my-vpn:vpn1:default:roci".networking;
      expected = null;
    };
}
