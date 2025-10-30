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
    expected = "serviceA/instance01/roleX/machine01";
  };
  test_check_scope_simple = {
    expr = clan-core.clanLib.exports.checkScope {
      serviceName = "serviceA";
      machineName = "machine01";
    } "serviceA///machine01";
    expected = "serviceA///machine01";
  };
  test_parse_scope_simple = {
    expr = clan-core.clanLib.exports.parseScope "serviceA///machine01";
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
          "serviceA///" = {
            foo = 42;
          };
          # "serviceB///" = { foo = 7; };
        };
    expected = {
      "serviceA///" = {
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
          "serviceA///" = {
            foo = 42;
          };
          "serviceA/iA//" = {
            foo = 42;
          };
          "serviceA/iA/default/" = {
            foo = 42;
          };
          "serviceA/iA/default/jon" = {
            foo = 42;
          };
          "serviceA/iA/default/sara" = {
            foo = 42;
          };
          "serviceB///" = {
            foo = 7;
          };
        }
    );
    expected = [
      "serviceA/iA/default/"
      "serviceA/iA/default/jon"
      "serviceA/iA/default/sara"
    ];
  };

  test_simple =
    let
      eval = clan-core.clanLib.clan {
        exports."///".foo = lib.mkForce eval.config.exports."///".bar;

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
            # config.exports
            manifest.name = "A";

            roles.default = {
              # TODO: Remove automapping
              # Currently exports are automapped
              # scopes "/service=A/instance=hello/role=default/machine=jon"
              # perInstance.exports.foo = 7;

              # New style:
              # Explizit scope
              # perInstance.exports."service=A/instance=hello/role=default/machine=jon".foo = 7;
              perInstance =
                {
                  machine,
                  exports,
                  mkExports,
                  ...
                }:
                {
                  # "A/${instanceName}/default/${machine.name}"
                  exports = mkExports {
                    foo = 7;
                    # Define export depending on B
                    # we dont know service names or machine names
                    # That means we need to collect them from the exports available
                    bar = exports."B/iB/default/${machine.name}".foo + 35;
                  };
                  # exports."A/${instanceName}/default/${machine.name}".

                  # default behavior
                  # exports = scope.mkExports { foo = 7; };

                  # We want to export things for different scopes from this scope;
                  # If this scope is used.
                  #
                  # Explicit scope; different from the function scope above
                  # exports = clanLib.scopedExport {
                  #   # Different role export
                  #   role = "peer";
                  #   serviceName = config.manifest.name;
                  #   inherit instanceName machineName;
                  # } { foo = 7; };
                };
            };

            perMachine =
              { machine, ... }:
              {
                #
                # exports = scope.mkExports { foo = 7; };
                # exports."A///${machine.name}".foo = 42;
                exports."A/iA2//${machine.name}".foo = 42;
                # exports."A/iA2//nonono".foo = 42;
              };

            # scope "/service=A/instance=??/role=??/machine=jon"
            # perMachine.exports.foo = 42;
            # xyz = config.exports."///".generators.foo.files.foofile.path;

            # # scope "/service=A/instance=??/role=??/machine=??"
            # # exports."///".foo = 10;

            # exports."///" = withInstance (head (attrNames config.instances)) ({ instanceName, ... }: {
            #   generators.foo = { config, ...}: {
            #     runtimeInputs = [ config.pkgs.hello ];
            #   };
            # });
            # clanInternals.allSystems.x86_64-linux.exports."///".generators.
            # clanInternals.exports.forSystem.x86_64-linux."///".generators.
            # # Cross compilation later :D
            # # clanInternals.allSystems.x86_64-linux.cross.aarch64-linux.exports."///".generators.

            # exports = lib.genAttrs (attrNames config.instances) (instanceName: {
            #   "A/${instanceName}//" = {

            #   };
            # });
          };
        ####### Service module "A"
        modules.service-B =
          { exports, ... }:
          {
            # config.exports
            manifest.name = "B";

            roles.default = {
              # TODO: Remove automapping
              # Currently exports are automapped
              # scopes "/service=A/instance=hello/role=default/machine=jon"
              # perInstance.exports.foo = 7;

              # New style:
              # Explizit scope
              # perInstance.exports."service=A/instance=hello/role=default/machine=jon".foo = 7;
              perInstance =
                { instanceName, machine, ... }:
                {
                  # TODO: Test non-existing scope
                  # define export depending on A
                  exports."B/${instanceName}/default/${machine.name}".foo =
                    exports."///".foo + exports."A/iA1/default/${machine.name}".foo;
                  # exports."B/B/default/jon".foo = exports."A/A/default/jon".foo;

                  # default behavior
                  # exports = scope.mkExports { foo = 7; };

                  # We want to export things for different scopes from this scope;
                  # If this scope is used.
                  #
                  # Explicit scope; different from the function scope above
                  # exports = clanLib.scopedExport {
                  #   # Different role export
                  #   role = "peer";
                  #   serviceName = config.manifest.name;
                  #   inherit instanceName machineName;
                  # } { foo = 7; };
                };
            };

            perMachine =
              { ... }:
              {
                # exports = scope.mkExports { foo = 7; };
                # exports."A///${machine.name}".foo = 42;
                # exports."B///".foo = 42;
              };

            # scope "/service=A/instance=??/role=??/machine=jon"
            # perMachine.exports.foo = 42;

            # scope "/service=A/instance=??/role=??/machine=??"
            exports."///".foo = 10;
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
        # <- inventory
        #
        # -> exports
        /**
          Current state
          {
            instances = {
              hello = { networking = null; };
            };
            machines = {
              jon = { networking = null; };
            };
          }
        */
        /**
          Target state: (Flat attribute set)

          tdlr;

          # roles / instance level definitions may not exist on their own
          # role and instance names are completely arbitrary.
          # For example what does it mean: this is a export for all "peer" roles of all service-instances? That would be magic on the roleName.
          # Or exports for all instances with name "ifoo" ? That would be magic on the instanceName.

          # Practical combinations
          # always include either the service name or the machine name

          exports = {
            # Clan level (1)
            "///" networks generators

            # Service anchored (8) : min 1 instance is needed ; machines may not exist
            "A///" <- service specific
            "A/instance//" <- instance of a service
            "A//peer/" <- role of a service
            "A/instance/peer/" <- instance+role of a service
            "A///machine" <- machine of a service
            "A/instance//machine" <- machine + instance of a service
            "A//role/machine" <- machine + role of a service
            "A/instance/role/machine" <- machine + role + instance of a service

            # Machine anchored (1 or 2)
            "///jon" <- this machine
            "A///jon" <- role on a machine (dupped with service anchored)

            # Unpractical; probably not needed (5)
            "//peer/jon" <- role on a machine
            "/instance//jon" <- role on a machine
            "/instance//" <- instance: All "foo" instances everywhere?
            "//role/" <- role: All "peer" roles everywhere?
            "/instance/role/" <- instance role: Applies to all services, whose instance name has "ifoo" and role is "peer" (double magic)

            # TODO: lazyattrs poc
          }
        */
      };
    in
    {
      inherit eval;
      expr = clan-core.clanLib.exports.selectExports { } eval.config.exports;
      expected = {
        "///" = {
          bar = 0;
          foo = 0;
        };
        "A/iA1/default/jon" = {
          bar = 42;
          foo = 7;
        };
        "A/iA1/default/sara" = {
          bar = 42;
          foo = 7;
        };
        "A/iA2//jon" = {
          bar = 0;
          foo = 42;
        };
        "A/iA2//sara" = {
          bar = 0;
          foo = 42;
        };
        "A/iA2/default/jon" = {
          bar = 42;
          foo = 7;
        };
        "A/iA2/default/sara" = {
          bar = 42;
          foo = 7;
        };
        "B/iB/default/jon" = {
          bar = 0;
          foo = 7;
        };
        "B/iB/default/sara" = {
          bar = 0;
          foo = 7;
        };
      };
    };
}
