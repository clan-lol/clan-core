{
  self,
  inputs,
  lib,
  ...
}:
let
  module = ./default.nix;
in
{
  clan.modules = {
    hello-world = module;
  };
  perSystem =
    { ... }:
    let
      # Module that contains the tests
      # This module adds:
      # - legacyPackages.<system>.evalTests-hello-world: The test attrset for nix-unit.
      # - legacyPackages.<system>.evalCheck-eval-tests-hello-world: The nix-unit derivation.
      # All eval checks are unified into checks.<system>.eval-tests (see checks/flake-module.nix).
      unit-test-module = (
        self.clanLib.test.flakeModules.makeEvalChecks {
          inherit module;
          inherit inputs;
          fileset = lib.fileset.unions [
            # The hello-world service being tested
            ../../clanServices/hello-world
            # Required modules
            ../../nixosModules
          ];
          testName = "hello-world";
          tests = ./tests/eval-tests.nix;
          # Optional arguments passed to the test
          testArgs = { };
        }
      );
    in
    {
      imports = [ unit-test-module ];

      /**
        1. Prepare the test vars
        nix run .#generate-test-vars -- clanServices/hello-world/tests/vm hello-service

        2. To run the test
        nix build .#checks.x86_64-linux.hello-service
      */
      clan.nixosTests.hello-service = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules.hello-service = module;
      };
    };
}
