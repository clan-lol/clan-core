{ clanLib, ... }:
{
  test_check_scope_simple = {
    expr = clanLib.exports.checkScope {
      serviceName = "serviceA";
      machineName = "machine01";
    } "serviceA:::machine01";
    expected = "serviceA:::machine01";
  };

  test_check_scope_all_parts = {
    expr = clanLib.exports.checkScope {
      serviceName = "serviceA";
      instanceName = "i1";
      roleName = "default";
      machineName = "machine01";
    } "serviceA:i1:default:machine01";
    expected = "serviceA:i1:default:machine01";
  };

  test_check_scope_with_whitelist = {
    expr = clanLib.exports.checkScope {
      serviceName = "serviceA";
      machineName = "machine01";
      whitelist = [ "serviceB:::machine02" ];
    } "serviceB:::machine02";
    expected = "serviceB:::machine02";
  };
}
