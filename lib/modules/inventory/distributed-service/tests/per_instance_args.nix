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
    roles.controller = { };
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
        extendSettings,
        machine,
        roles,
        ...
      }:
      let
        finalSettings = extendSettings {
          # Sometimes we want to create a default settings set depending on the machine config.
          # Note: Other machines cannot depend on this settings. We must assign a new name to the settings.
          # And thus the new value is not accessible by other machines.
          timeout = lib.mkOverride 10 "config.thing";
        };
      in
      {
        options.passthru = lib.mkOption {
          default = {
            inherit
              instanceName
              settings
              machine
              roles
              ;

            # We are double vendoring the settings
            # To test that we can do it indefinitely
            vendoredSettings = finalSettings;
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
        input = "self";
      };
      roles.peer.machines.jon = {
        settings.timeout = lib.mkForce "foo-peer-jon";
      };
      roles.peer = {
        settings.timeout = "foo-peer";
      };
      roles.controller.machines.jon = { };
    };
    instances."instance_bar" = {
      module = {
        name = "A";
        input = "self";
      };
      roles.peer.machines.jon = {
        settings.timeout = "bar-peer-jon";
      };
    };
    # TODO: move this into a seperate test.
    # Seperate out the check that this module is never imported
    # import the module "B" (undefined)
    # All machines have this instance
    instances."instance_zaza" = {
      module = {
        name = "B";
        input = null;
      };
      roles.peer.tags.all = { };
    };
  };

  /*
    1 { imports = [ { instanceName = "instance_foo"; machine = { name = "jon"; roles = [ "controller" "pe 1 null
    . er" ]; }; roles = { controller = { machines = { jon = { settings = { }; }; }; settings = { }; }; pe .
    . er = { machines = { jon = { settings = { timeout = "foo-peer-jon"; }; }; }; settings = { timeout =  .
    . "foo-peer"; }; }; }; settings = { timeout = "foo-peer-jon"; }; vendoredSettings = { timeout = "conf .
    . ig.thing"; }; } ]; }                                                                                .
  */
in
{
  # settings should evaluate
  test_per_instance_arguments = {
    expr = {
      instanceName =
        res.importedModulesEvaluated.self-A.result.allRoles.peer.allInstances."instance_foo".allMachines.jon.passthru.instanceName;

      # settings are specific.
      # Below we access:
      # instance = instance_foo
      # roles = peer
      # machines = jon
      settings =
        res.importedModulesEvaluated.self-A.result.allRoles.peer.allInstances.instance_foo.allMachines.jon.passthru.settings;
      machine =
        res.importedModulesEvaluated.self-A.result.allRoles.peer.allInstances.instance_foo.allMachines.jon.passthru.machine;
      roles =
        res.importedModulesEvaluated.self-A.result.allRoles.peer.allInstances.instance_foo.allMachines.jon.passthru.roles;
    };
    expected = {
      instanceName = "instance_foo";
      machine = {
        name = "jon";
        roles = [
          "controller"
          "peer"
        ];
      };
      roles = {
        controller = {
          machines = {
            jon = {
              settings = { };
            };
          };
        };
        peer = {
          machines = {
            jon = {
              settings = {
                timeout = "foo-peer-jon";
              };
            };
          };
        };
      };
      settings = {
        timeout = "foo-peer-jon";
      };
    };
  };

  # TODO: Cannot be tested like this anymore
  test_per_instance_settings_vendoring = {
    x = res.importedModulesEvaluated.self-A;
    expr =
      res.importedModulesEvaluated.self-A.result.allRoles.peer.allInstances.instance_foo.allMachines.jon.passthru.vendoredSettings;
    expected = {
      timeout = "config.thing";
    };
  };
}
