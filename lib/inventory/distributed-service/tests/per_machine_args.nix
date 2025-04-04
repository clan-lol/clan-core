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
        nixosModule = {
          inherit instances machine;
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
    instances."instance_zaza" = {
      module = {
        name = "B";
      };
      roles.peer.tags.all = { };
    };
  };

  filterInternals = lib.filterAttrs (n: _v: !lib.hasPrefix "_" n);
in

{

  # settings should evaluate
  test_per_machine_receives_instance_settings = {
    inherit res;
    expr = {
      hasMachineSettings =
        res.importedModulesEvaluated.self-A.config.result.allMachines.jon.nixosModule.instances.instance_foo.roles.peer.machines.jon
        ? settings;

      # settings are specific.
      # Below we access:
      # instance = instance_foo
      # roles = peer
      # machines = jon
      specificMachineSettings = filterInternals res.importedModulesEvaluated.self-A.config.result.allMachines.jon.nixosModule.instances.instance_foo.roles.peer.machines.jon.settings;

      hasRoleSettings =
        res.importedModulesEvaluated.self-A.config.result.allMachines.jon.nixosModule.instances.instance_foo.roles.peer
        ? settings;

      # settings are specific.
      # Below we access:
      # instance = instance_foo
      # roles = peer
      # machines = *
      specificRoleSettings = filterInternals res.importedModulesEvaluated.self-A.config.result.allMachines.jon.nixosModule.instances.instance_foo.roles.peer.settings;
    };
    expected = {
      hasMachineSettings = true;
      specificMachineSettings = {
        timeout = "foo-peer-jon";
      };
      hasRoleSettings = true;
      specificRoleSettings = {
        timeout = "foo-peer";
      };
    };
  };
}
