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
      # - legacyPackages.<system>.evalTests-types: The test attrset for nix-unit.
      # - legacyPackages.<system>.evalCheck-eval-tests-types: The nix-unit derivation.
      # All eval checks are unified into checks.<system>.eval-tests (see checks/flake-module.nix).
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
