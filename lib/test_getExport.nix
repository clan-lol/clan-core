{ clan-core }:
{
  test_get_export = {
    expr =
      clan-core.clanLib.exports.getExport
        {
          serviceName = "serviceA";
          instanceName = "iA";
          roleName = "default";
          machineName = "jon";
        }
        {
          "serviceA:iA:default:jon" = {
            foo = 42;
            bar = 7;
          };
          "serviceA:iA:default:sara" = {
            foo = 10;
          };
        };
    expected = {
      foo = 42;
      bar = 7;
    };
  };

  test_get_export_service_level = {
    expr =
      clan-core.clanLib.exports.getExport
        {
          serviceName = "serviceA";
        }
        {
          "serviceA:::" = {
            config = "global-service-config";
            port = 8080;
          };
          "serviceA:::machine01" = {
            foo = 99;
          };
        };
    expected = {
      config = "global-service-config";
      port = 8080;
    };
  };

  test_get_export_machine_level = {
    expr =
      clan-core.clanLib.exports.getExport
        {
          machineName = "machine01";
        }
        {
          ":::machine01" = {
            hostname = "machine01.example.com";
            ip = "192.168.1.10";
          };
          "serviceA:::machine01" = {
            other = "data";
          };
        };
    expected = {
      hostname = "machine01.example.com";
      ip = "192.168.1.10";
    };
  };
}
