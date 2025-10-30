{ lib, createTestClan }:
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
    roles.server.interface =
      { lib, ... }:
      {
        options.timeout = lib.mkOption {
          type = lib.types.submodule;
        };
      };

    perMachine =
      { instances, machine, ... }:
      {
        options.passthru = lib.mkOption {
          default = {
            inherit instances machine;
          };
        };
      };
  };
  machines = {
    jon = { };
    sara = { };
  };
  res = createTestClan {
    inherit modules;
    inventory = {

      inherit machines;
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
      instances."instance_zaza" = {
        module = {
          name = "B";
          input = null;
        };
        roles.peer.tags.all = { };
      };
    };
  };
in

{

  # settings should evaluate
  test_per_machine_receives_instance_settings = {
    inherit res;
    expr = {
      hasMachineSettings =
        res.config._services.mappedServices.self-A.result.allMachines.jon.passthru.instances.instance_foo.roles.peer.machines.jon
        ? settings;

      # settings are specific.
      # Below we access:
      # instance = instance_foo
      # roles = peer
      # machines = jon
      specificMachineSettings =
        res.config._services.mappedServices.self-A.result.allMachines.jon.passthru.instances.instance_foo.roles.peer.machines.jon.settings;

      hasRoleSettings =
        res.config._services.mappedServices.self-A.result.allMachines.jon.passthru.instances.instance_foo.roles.peer
        ? settings;

      # settings are specific.
      # Below we access:
      # instance = instance_foo
      # roles = peer
      # machines = *
      specificRoleSettings =
        res.config._services.mappedServices.self-A.result.allMachines.jon.passthru.instances.instance_foo.roles.peer;
    };
    expected = {
      hasMachineSettings = true;
      hasRoleSettings = true;
      specificMachineSettings = {
        timeout = "foo-peer-jon";
      };
      specificRoleSettings = {
        machines = {
          jon = {
            settings = {
              timeout = "foo-peer-jon";
            };
          };
        };
        settings = {
          timeout = "foo-peer";
        };
      };
    };
  };
}
