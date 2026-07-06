{ createTestClan, lib, ... }:
let
  res = createTestClan {
    modules."A" = {
      _class = "clan.service";
      manifest = {
        name = "network";
      };
      roles.peer.interface =
        { lib, ... }:
        {
          options.timeout = lib.mkOption {
            type = lib.types.int;
          };
        };
      roles.controller.interface =
        { lib, ... }:
        {
          options.maxPeers = lib.mkOption {
            type = lib.types.int;
          };
        };
    };
    inventory = {

      machines = {
        jon = { };
        sara = { };
      };
      instances."instance_foo" = {
        module = {
          name = "A";
          input = "self";
        };
        # Settings for both jon and sara
        roles.peer.settings = {
          timeout = 40;
        };
        # Jon overrides timeout
        roles.peer.machines.jon = {
          settings.timeout = lib.mkForce 42;
        };
        roles.peer.machines.sara = { };
      };
    };
  };

  config = res.config._services.allServices.self-A;

  #
  applySettings =
    instanceName: instance:
    lib.mapAttrs (roleName: role: {
      machines = lib.mapAttrs (machineName: _v: {
        settings =
          config.instances.${instanceName}.roles.${roleName}.machines.${machineName}.finalSettings.config;
      }) role.machines;
    }) instance.roles;

  mapSettings = lib.mapAttrs applySettings config.instances;
in
{
  test_simple = {
    expr = mapSettings;
    expected = {
      instance_foo = {
        peer = {
          machines = {
            jon = {
              settings = {
                timeout = 42;
              };
            };
            sara = {
              settings = {
                timeout = 40;
              };
            };
          };
        };
      };
    };
  };

  test_tag_settings =
    let
      res2 = createTestClan {
        modules."B" = {
          _class = "clan.service";
          manifest = {
            name = "tag-test";
          };
          roles.peer.interface =
            { lib, ... }:
            {
              options.timeout = lib.mkOption {
                type = lib.types.int;
              };
            };
        };
        inventory = {
          machines = {
            jon = {
              tags = [ "special" ];
            };
            sara = { };
          };
          instances.inst = {
            module = {
              name = "B";
              input = "self";
            };
            roles.peer.machines.jon = { };
            roles.peer.machines.sara = { };
            roles.peer.settings.timeout = 40;
            roles.peer.tags.special.settings.timeout = lib.mkForce 50;
          };
        };
      };
      map2 = lib.mapAttrs (
        instanceName: instance:
        lib.mapAttrs (roleName: role: {
          machines = lib.mapAttrs (machineName: _v: {
            settings =
              config.instances.${instanceName}.roles.${roleName}.machines.${machineName}.finalSettings.config;
          }) role.machines;
        }) instance.roles
      ) config.instances;
      config = res2.config._services.allServices."self-B";
    in
    {
      expr = map2;
      expected = {
        inst = {
          peer = {
            machines = {
              jon = {
                settings = {
                  timeout = 50;
                };
              };
              sara = {
                settings = {
                  timeout = 40;
                };
              };
            };
          };
        };
      };
    };
}
