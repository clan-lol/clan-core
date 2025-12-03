{ clanLib, ... }:
{
  test_parse_scope_simple = {
    expr = clanLib.parseScope "serviceA:::machine01";
    expected = {
      serviceName = "serviceA";
      instanceName = "";
      roleName = "";
      machineName = "machine01";

    };
  };

  test_parse_scope_full = {
    expr = clanLib.parseScope "serviceA:i1:default:machine01";
    expected = {
      serviceName = "serviceA";
      instanceName = "i1";
      roleName = "default";
      machineName = "machine01";
    };
  };

  test_parse_scope_global = {
    expr = clanLib.parseScope ":::";
    expected = {
      serviceName = "";
      instanceName = "";
      roleName = "";
      machineName = "";
    };
  };
}
