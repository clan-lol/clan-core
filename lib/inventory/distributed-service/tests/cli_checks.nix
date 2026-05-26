{
  createTestClan,
}:
let
  # Helper: create a service module with constraints
  mkServiceModule =
    {
      name,
      constraints ? { },
      roles ? {
        default = { };
      },
    }:
    {
      _class = "clan.service";
      manifest = {
        inherit name constraints;
      };
      inherit roles;
    };
in
{
  # No constraints: empty cliChecks
  test_no_constraints =
    let
      res = createTestClan {
        modules."svc" = mkServiceModule { name = "svc"; };
        inventory.machines.jon = { };
        inventory.instances."my-svc" = {
          module.name = "svc";
          module.input = "self";
          roles.default.machines.jon = { };
        };
      };
    in
    {
      inherit res;
      expr = res.config.clanInternals.cliChecks;
      expected = [ ];
    };

  # maxInstances = 1, one instance : passes
  test_maxInstances_pass =
    let
      res = createTestClan {
        modules."svc" = mkServiceModule {
          name = "svc";
          constraints.maxInstances = 1;
        };
        inventory.machines.jon = { };
        inventory.instances."my-svc" = {
          module.name = "svc";
          module.input = "self";
          roles.default.machines.jon = { };
        };
      };
    in
    {
      inherit res;
      expr = res.config.clanInternals.cliChecks;
      expected = [ ];
    };

  # maxInstances = 1, two instances : error
  test_maxInstances_fail =
    let
      res = createTestClan {
        modules."svc" = mkServiceModule {
          name = "svc";
          constraints.maxInstances = 1;
        };
        inventory.machines.jon = { };
        inventory.instances."inst-a" = {
          module.name = "svc";
          module.input = "self";
          roles.default.machines.jon = { };
        };
        inventory.instances."inst-b" = {
          module.name = "svc";
          module.input = "self";
          roles.default.machines.jon = { };
        };
      };
    in
    {
      inherit res;
      expr = res.config.clanInternals.cliChecks;
      expected = [
        {
          id = "svc-maxInstances";
          message = "Service 'svc' allows at most 1 instance(s) but 2 are defined.";
          severity = "error";
        }
      ];
    };

  # minMachines = 1 on role, zero machines assigned : error
  test_minMachines_fail =
    let
      res = createTestClan {
        modules."svc" = mkServiceModule {
          name = "svc";
          constraints.roles.server = {
            minMachines = 1;
          };
          roles.server = { };
          roles.default = { };
        };
        inventory.machines.jon = { };
        inventory.instances."my-svc" = {
          module.name = "svc";
          module.input = "self";
          roles.default.machines.jon = { };
        };
      };
    in
    {
      inherit res;
      expr = res.config.clanInternals.cliChecks;
      expected = [
        {
          id = "svc-my-svc-server-minMachines";
          message = "Role 'server' of service 'svc' instance 'my-svc' requires at least 1 machine(s) but 0 are assigned.";
          severity = "error";
        }
      ];
    };

  # maxMachines = 1 on role, two machines : error
  test_maxMachines_fail =
    let
      res = createTestClan {
        modules."svc" = mkServiceModule {
          name = "svc";
          constraints.roles.default = {
            maxMachines = 1;
          };
        };
        inventory.machines.jon = { };
        inventory.machines.sara = { };
        inventory.instances."my-svc" = {
          module.name = "svc";
          module.input = "self";
          roles.default.machines.jon = { };
          roles.default.machines.sara = { };
        };
      };
    in
    {
      inherit res;
      expr = res.config.clanInternals.cliChecks;
      expected = [
        {
          id = "svc-my-svc-default-maxMachines";
          message = "Role 'default' of service 'svc' instance 'my-svc' allows at most 1 machine(s) but 2 are assigned.";
          severity = "error";
        }
      ];
    };

  # minMachines = 1, maxMachines = 1 on role, one machine : passes
  test_exact_machine_count_pass =
    let
      res = createTestClan {
        modules."svc" = mkServiceModule {
          name = "svc";
          constraints.roles.default = {
            minMachines = 1;
            maxMachines = 1;
          };
        };
        inventory.machines.jon = { };
        inventory.instances."my-svc" = {
          module.name = "svc";
          module.input = "self";
          roles.default.machines.jon = { };
        };
      };
    in
    {
      inherit res;
      expr = res.config.clanInternals.cliChecks;
      expected = [ ];
    };
}
