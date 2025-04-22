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
    { pkgs, ... }:
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

      /**
        1. Prepare the test vars
        nix run .#generate-test-vars -- clanServices/hello-world/tests/vm hello-service

        2. To run the test
        nix build .#checks.x86_64-linux.hello-service
      */
      checks =
        # Currently we don't support nixos-integration tests on darwin
        lib.optionalAttrs (pkgs.stdenv.isLinux) {
          hello-service = import ./tests/vm/default.nix {
            inherit module;
            inherit self inputs pkgs;
            clanLib = self.clanLib;
          };
        };
    };
}
