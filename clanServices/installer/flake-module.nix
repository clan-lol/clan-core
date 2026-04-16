{
  self,
  inputs,
  lib,

  ...
}:
let
  module = lib.modules.importApply ./default.nix { clanPackages = self.packages; };
in
{
  clan.modules = {
    installer = module;
  };
  perSystem =
    { ... }:
    let
      # Module that contains the tests
      # This module adds:
      # - legacyPackages.<system>.eval-tests-hello-world
      # - checks.<system>.eval-tests-hello-world
      unit-test-module = (
        self.clanLib.test.flakeModules.makeEvalChecks {
          inherit module;
          inherit inputs;
          fileset = lib.fileset.unions [
            # The hello-world service being tested
            ../../clanServices/installer
            # Required modules
            ../../nixosModules
          ];
          testName = "installer";
          tests = ./tests/eval-tests.nix;
          # Optional arguments passed to the test
          testArgs = { };
        }
      );
    in
    {
      imports = [ unit-test-module ];
    };
}
