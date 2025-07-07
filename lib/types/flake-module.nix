{
  self,
  inputs,
  lib,
  ...
}:
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
          inherit inputs;
          fileset = lib.fileset.unions [
            # Only lib is needed for type tests
            ../../lib
          ];
          testName = "types";
          tests = ./tests.nix;
          # Optional arguments passed to the test
          testArgs = { };
        }
      );
    in
    {
      imports = [ test-types-module ];
    };
}
