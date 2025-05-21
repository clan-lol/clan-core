{ self, inputs, ... }:
{
  perSystem =
    { ... }:
    let
      # Module that contains the tests
      # This module adds:
      # - legacyPackages.<system>.eval-tests-hello-world
      # - checks.<system>.eval-tests-hello-world
      test-types-module = (
        self.clanLib.test.flakeModules.makeEvalChecks {
          module = throw "";
          inherit self inputs;
          testName = "types";
          tests = ./tests.nix;
          # Optional arguments passed to the test
          testArgs = { };
        }
      );
    in
    {
      imports = [ test-types-module ];
      legacyPackages.xxx = { };
    };
}
