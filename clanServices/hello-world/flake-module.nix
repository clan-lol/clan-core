{
  self,
  inputs,
  lib,
  ...
}:
let
  module = lib.modules.importApply ./default.nix {
    inherit (self) packages;
  };
in
{
  clan.inventory.modules = {
    hello-world = module;
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
          inherit self inputs;
          testName = "hello-world";
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
