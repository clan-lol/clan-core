{ lib, callInventoryAdapter }:
let
  # Authored module
  # A minimal module looks like this
  # It isn't exactly doing anything but it's a valid module that produces an output
  modules."A" = {
    _class = "clan.service";
    manifest = {
      name = "network";
    };
    # Define two roles with unmergeable interfaces
    # Both define some 'timeout' but with completely different types.
    roles.peer.interface =
      { lib, ... }:
      {
        options.timeout = lib.mkOption {
          type = lib.types.str;
        };
      };

    roles.peer.perInstance =
      {
        instanceName,
        settings,
        machine,
        ...
      }:
      let
        settings1 = settings {
          # Sometimes we want to create a default settings set depending on the machine config.
          # Note: Other machines cannot depend on this settings. We must assign a new name to the settings.
          # And thus the new value is not accessible by other machines.
          timeout = lib.mkOverride 10 "config.blah";
        };
      in
      {
        nixosModule = {
          inherit instanceName settings machine;

          # We are double vendoring the settings
          # To test that we can do it indefinitely
          vendoredSettings = settings1 {
            # Sometimes we want to create a default settings set depending on the machine config.
            # Note: Other machines cannot depend on this settings. We must assign a new name to the settings.
            # And thus the new value is not accessible by other machines.
            timeout = lib.mkOverride 5 "config.thing";
          };
        };
      };
  };
  machines = {
    jon = { };
    sara = { };
  };
  res = callInventoryAdapter {
    inherit modules machines;
    instances."instance_foo" = {
      module = {
        name = "A";
      };
      roles.peer.machines.jon = {
        settings.timeout = lib.mkForce "foo-peer-jon";
      };
      roles.peer = {
        settings.timeout = "foo-peer";
      };
    };
    instances."instance_bar" = {
      module = {
        name = "A";
      };
      roles.peer.machines.jon = {
        settings.timeout = "bar-peer-jon";
      };
    };
    # import the module "B" (undefined)
    # All machines have this instance
    instances."instance_zaza" = {
      module = {
        name = "B";
      };
      roles.peer.tags.all = { };
    };
  };

  filterInternals = lib.filterAttrs (n: _v: !lib.hasPrefix "_" n);

  # Replace internal attributes ('_' prefix)
  # So we catch their presence but don't check the value
  mapInternalsRecursive = lib.mapAttrsRecursive (
    path: v:
    let
      name = lib.last path;
    in
    if !lib.hasPrefix "_" name then v else name
  );
in
{
  # settings should evaluate
  test_per_instance_arguments = {
    expr = {
      instanceName =
        res.evals.self-A.config.result.allRoles.peer.allInstances."instance_foo".allMachines.jon.nixosModule.instanceName;

      # settings are specific.
      # Below we access:
      # instance = instance_foo
      # roles = peer
      # machines = jon
      settings = filterInternals res.evals.self-A.config.result.allRoles.peer.allInstances.instance_foo.allMachines.jon.nixosModule.settings;
      machine = mapInternalsRecursive res.evals.self-A.config.result.allRoles.peer.allInstances.instance_foo.allMachines.jon.nixosModule.machine;

      # hasRoleSettings =
      #   res.evals.self-A.config.result.allMachines.jon.nixosModule.instance_foo.roles.peer ? settings;

      # # settings are specific.
      # # Below we access:
      # # instance = instance_foo
      # # roles = peer
      # # machines = *
      # specificRoleSettings = filterInternals res.evals.self-A.config.result.allMachines.jon.nixosModule.instance_foo.roles.peer.settings;
    };
    expected = {
      instanceName = "instance_foo";
      settings = {
        timeout = "foo-peer-jon";
      };
      machine = {
        name = "jon";
        roles = {
          peer = {
            machines = {
              jon = {
                settings = {
                  __functor = "__functor";
                  timeout = "foo-peer-jon";
                };
              };
            };
            settings = {
              __functor = "__functor";
              timeout = "foo-peer";
            };
          };
        };
      };
    };
  };

  test_per_instance_settings_vendoring = {
    expr =
      mapInternalsRecursive
        res.evals.self-A.config.result.allRoles.peer.allInstances."instance_foo".allMachines.jon.nixosModule.vendoredSettings;
    expected = {
      # Returns another override
      __functor = "__functor";
      timeout = "config.thing";
    };
  };
}
