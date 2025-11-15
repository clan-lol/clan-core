{ clan-core, ... }:
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

  test_build_scope_key_service_only = {
    expr = clan-core.clanLib.exports.buildScopeKey {
      serviceName = "serviceA";
    };
    expected = "serviceA:::";
  };

  test_build_scope_key_machine_only = {
    expr = clan-core.clanLib.exports.buildScopeKey {
      machineName = "machine01";
    };
    expected = ":::machine01";
  };
}
