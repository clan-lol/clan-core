{
  lib,
  self,
  inputs,
  ...
}:
let
  module = ./default.nix;
in
{
  clan.modules.zerotier = module;
  perSystem =
    { ... }:
    let
      unit-test-module = (
        self.clanLib.test.flakeModules.makeEvalChecks {
          inherit module;
          inherit inputs;
          fileset = lib.fileset.unions [
            # The zerotier service being tested
            ../../clanServices/zerotier
            # Required modules
            ../../nixosModules/clanCore
            ../../nixosModules/machineModules
            # Dependencies
            ../../pkgs/clan-cli
            ../../pkgs/zerotier-tools
          ];
          testName = "zerotier";
          tests = ./tests/eval-tests.nix;
          testArgs = { };
        }
      );
    in
    {
      imports = [
        unit-test-module
      ];

      clan.nixosTests.zerotier = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules.zerotier = module;
      };

      clan.nixosTests.zerotier-multi-instance = {
        imports = [ ./tests/vm-multi-instance/default.nix ];

        clan.modules.zerotier = module;
      };
    };
}
