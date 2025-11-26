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
                type = lib.types.str;
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
            manifest.traits = [ "bar" ];

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
}
