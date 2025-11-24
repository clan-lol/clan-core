{
  clanLib,
  ...
}:
{
  test_check_exports = {
    expr =
      clanLib.exports.checkExports
        {
          serviceName = "serviceA";
        }
        {
          "serviceA:::" = {
            foo = 42;
          };
        };
    expected = {
      "serviceA:::" = {
        foo = 42;
      };
    };
  };

  test_check_exports_multiple = {
    expr =
      clanLib.exports.checkExports
        {
          serviceName = "serviceA";
        }
        {
          "serviceA:::" = {
            foo = 42;
          };
          "serviceA:::machine01" = {
            bar = 7;
          };
          "serviceA:i1:default:machine02" = {
            baz = 99;
          };
        };
    expected = {
      "serviceA:::" = {
        foo = 42;
      };
      "serviceA:::machine01" = {
        bar = 7;
      };
      "serviceA:i1:default:machine02" = {
        baz = 99;
      };
    };
  };

  test_check_exports_with_machine = {
    expr =
      clanLib.exports.checkExports
        {
          serviceName = "serviceA";
          machineName = "machine01";
        }
        {
          "serviceA:::machine01" = {
            value = 123;
          };
        };
    expected = {
      "serviceA:::machine01" = {
        value = 123;
      };
    };
  };
}
