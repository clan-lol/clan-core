{
  self,
  lib,
  inputs,
  ...
}:
let
  module = ./default.nix;
in
{
  clan.modules = {
    syncthing = module;
  };
  perSystem =
    let
      unit-test-module = (
        self.clanLib.test.flakeModules.makeEvalChecks {
          inherit module;
          inherit inputs;
          fileset = lib.fileset.unions [
            ../../clanServices/syncthing
            # Required modules
            ../../nixosModules/clanCore
            ../../nixosModules/machineModules
            # Dependencies like clan-cli
            ../../pkgs/clan-cli
          ];
          testName = "syncthing";
          tests = ./tests/eval-tests.nix;
          testArgs = { };
        }
      );
    in
    { ... }:
    {
      imports = [
        unit-test-module
      ];
      /**
        1. Prepare the test vars
        nix run .#generate-test-vars -- clanServices/syncthing/tests/vm syncthing-service

        2. To run the test
        nix build .#checks.x86_64-linux.syncthing-service
      */
      clan.nixosTests.syncthing-service = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules.syncthing-service = module;
      };
    };
}
