{ clanLib, lib }:
{
  test_select_exports = {
    expr = lib.attrNames (
      clanLib.selectExports
        (s: s.serviceName == "serviceA" && s.instanceName == "iA" && s.roleName == "default")
        {
          "serviceA:::" = {
            foo = 42;
          };
          "serviceA:iA::" = {
            foo = 42;
          };
          "serviceA:iA:default:" = {
            foo = 42;
          };
          "serviceA:iA:default:jon" = {
            foo = 42;
          };
          "serviceA:iA:default:sara" = {
            foo = 42;
          };
          "serviceB:::" = {
            foo = 7;
          };
        }
    );
    expected = [
      "serviceA:iA:default:"
      "serviceA:iA:default:jon"
      "serviceA:iA:default:sara"
    ];
  };

  test_select_exports_by_machine = {
    expr = lib.attrNames (
      clanLib.selectExports (s: s.machineName == "jon") {
        "serviceA:::jon" = {
          foo = 1;
        };
        "serviceA:iA:default:jon" = {
          foo = 2;
        };
        "serviceB:iB:peer:jon" = {
          foo = 3;
        };
        "serviceA:::sara" = {
          foo = 4;
        };
        ":::global" = {
          foo = 5;
        };
      }
    );
    expected = [
      "serviceA:::jon"
      "serviceA:iA:default:jon"
      "serviceB:iB:peer:jon"
    ];
  };

  test_select_exports_by_service_only = {
    expr = lib.attrNames (
      clanLib.selectExports (s: s.serviceName == "serviceA") {
        "serviceA:::" = {
          foo = 1;
        };
        "serviceA:::jon" = {
          foo = 2;
        };
        "serviceA:iA:peer:machineA" = {
          foo = 3;
        };
        "serviceB:iB:peer:machineB" = {
          foo = 4;
        };
        ":::global" = {
          foo = 5;
        };
      }
    );
    expected = [
      "serviceA:::"
      "serviceA:::jon"
      "serviceA:iA:peer:machineA"
    ];
  };

  test_select_exports_by_query = {
    expr = lib.attrNames (
      clanLib.exports.selectExports (scope: scope.serviceName != "A") {
        "A:::" = 1;
        "A:::jon" = 2;
        "A:iA:peer:jon" = 3;
        "B:iB:peer:jon" = 4;
        "C:iC:peer:jon" = throw "Error";
      }
    );
    expected = [
      "B:iB:peer:jon"
      "C:iC:peer:jon"
    ];
  };
}
