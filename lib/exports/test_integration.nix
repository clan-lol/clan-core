{ clanLib, lib }:
{
  test_simple =
    let
      eval = clanLib.clan {
        exports."B:::".foo = lib.mkForce eval.config.exports."B:::".bar;

        directory = ./.;
        self = {
          clan = eval.config;
          inputs = { };
        };

        machines.jon = { };
        machines.sara = { };

        exportInterfaces = lib.mkForce ({
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
                type = lib.types.int;
              };
            };
        });

        ####### Service module "A"
        modules.service-A =
          { ... }:
          {
            manifest.name = "A";
            manifest.traits = [
              "networking"
              "peer"
            ];

            roles.default = {
              perInstance =
                {
                  ...
                }:
                {
                  # exports = mkExports {
                  #   imports = [
                  #     # eval.config.exportInterfaces.foo
                  #     # eval.config.exportInterfaces.bar
                  #   ];
                  #   foo = 7;
                  #   # bar.opt = exports."B:iB:default:${machine.name}".foo + 35;
                  # };
                };
            };

            perMachine =
              { mkExports, ... }:
              {
                exports = mkExports {
                  # imports = [
                  #   eval.config.exportInterfaces.networking
                  # ];
                  networking.host = "42";
                };

                # exports =
                #   mkExports
                #     [
                #       eval.config.exportInterfaces.foo
                #     ]
                #     {

                #       foo.opt = "42";
                #     };
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
                    foo = exports."B:::".foo + exports."A:iA1:default:${machine.name}".foo;
                  };
                };
            };
            exports."B:::".foo = 10;
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
          # instances.iB = {
          #   module.name = "service-B";
          #   module.input = "self";
          #   roles.default.tags = [ "all" ];
          # };
        };
      };
    in
    {
      inherit eval;
      expr = clanLib.selectExports (_: true) eval.config.exports;
      expected = {
        "B:::" = {
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
