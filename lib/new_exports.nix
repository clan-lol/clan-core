{
  clan-core,
  lib,
}:
# TODO: Unit tests for every helper
{
  test_build_scope_key = {
    expr = clan-core.clanLib.exports.buildScopeKey {
      serviceName = "serviceA";
      instanceName = "instance01";
      roleName = "roleX";
      machineName = "machine01";
    };
    expected = "serviceA:instance01:roleX:machine01";
  };
  test_check_scope_simple = {
    expr = clan-core.clanLib.exports.checkScope {
      serviceName = "serviceA";
      machineName = "machine01";
    } "serviceA:::machine01";
    expected = "serviceA:::machine01";
  };
  test_parse_scope_simple = {
    expr = clan-core.clanLib.exports.parseScope "serviceA:::machine01";
    expected = {
      serviceName = "serviceA";
      instanceName = "";
      roleName = "";
      machineName = "machine01";

    };
  };
  test_check_exports = {
    expr =
      clan-core.clanLib.exports.checkExports
        {
          serviceName = "serviceA";
        }
        {
          "serviceA:::" = {
            foo = 42;
          };
        };
    expected = {
      "serviceA:::" = {
        foo = 42;
      };
    };
  };

  test_select_exports = {
    expr = lib.attrNames (
      clan-core.clanLib.exports.selectExports
        {
          serviceName = "serviceA";
          instanceName = "iA";
          roleName = "default";
        }
        {
          "serviceA:::" = {
            foo = 42;
          };
          "serviceA:iA::" = {
            foo = 42;
          };
          "serviceA:iA:default:" = {
            foo = 42;
          };
          "serviceA:iA:default:jon" = {
            foo = 42;
          };
          "serviceA:iA:default:sara" = {
            foo = 42;
          };
          "serviceB:::" = {
            foo = 7;
          };
        }
    );
    expected = [
      "serviceA:iA:default:"
      "serviceA:iA:default:jon"
      "serviceA:iA:default:sara"
    ];
  };

  test_get_export = {
    expr =
      clan-core.clanLib.exports.getExport
        {
          serviceName = "serviceA";
          instanceName = "iA";
          roleName = "default";
          machineName = "jon";
        }
        {
          "serviceA:iA:default:jon" = {
            foo = 42;
            bar = 7;
          };
          "serviceA:iA:default:sara" = {
            foo = 10;
          };
        };
    expected = {
      foo = 42;
      bar = 7;
    };
  };

  test_simple =
    let
      eval = clan-core.clanLib.clan {
        exports.":::".foo = lib.mkForce eval.config.exports.":::".bar;

        directory = ./.;
        self = {
          clan = eval.config;
          inputs = { };
        };

        machines.jon = { };
        machines.sara = { };

        exportsModule =
          { lib, ... }:
          {
            options.foo = lib.mkOption {
              type = lib.types.number;
              default = 0;
            };
            options.bar = lib.mkOption {
              type = lib.types.number;
              default = 0;
            };
          };

        ####### Service module "A"
        modules.service-A =
          { ... }:
          {
            manifest.name = "A";

            roles.default = {
              perInstance =
                {
                  machine,
                  exports,
                  mkExports,
                  ...
                }:
                {
                  exports = mkExports {
                    foo = 7;
                    bar = exports."B:iB:default:${machine.name}".foo + 35;
                  };
                };
            };

            perMachine =
              { mkExports, ... }:
              {
                exports = mkExports { foo = 42; };
              };
          };
        ####### Service module "A"
        modules.service-B =
          { exports, ... }:
          {
            manifest.name = "B";

            roles.default = {
              perInstance =
                {
                  machine,
                  mkExports,
                  ...
                }:
                {
                  exports = mkExports {
                    foo = exports.":::".foo + exports."A:iA1:default:${machine.name}".foo;
                  };
                };
            };
            exports.":::".foo = 10;
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
      expr = clan-core.clanLib.exports.selectExports { } eval.config.exports;
      expected = {
        ":::" = {
          bar = 0;
          foo = 0;
        };
        "A:::jon" = {
          bar = 0;
          foo = 42;
        };
        "A:::sara" = {
          bar = 0;
          foo = 42;
        };
        "A:iA1:default:jon" = {
          bar = 42;
          foo = 7;
        };
        "A:iA1:default:sara" = {
          bar = 42;
          foo = 7;
        };
        "A:iA2:default:jon" = {
          bar = 42;
          foo = 7;
        };
        "A:iA2:default:sara" = {
          bar = 42;
          foo = 7;
        };
        "B:iB:default:jon" = {
          bar = 0;
          foo = 7;
        };
        "B:iB:default:sara" = {
          bar = 0;
          foo = 7;
        };
      };
    };
}
