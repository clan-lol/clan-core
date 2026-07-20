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
    { pkgs, config, ... }:
    let
      unit-test-module = (
        self.clanLib.test.flakeModules.makeEvalChecks {
          inherit module;
          inherit inputs;
          fileset = lib.fileset.unions [
            # The service itself
            ./.
            # Dependencies
            ../../nixosModules/clanCore
            ../../nixosModules/machineModules
            # ../../pkgs/clan-cli
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
      # Add to packages so it gets built in CI
      packages.zerotier-tools = pkgs.callPackage ./pkgs/zerotier-tools { };
      packages.zerotierone = pkgs.callPackage ./pkgs/zerotierone { };

      checks = config.packages.zerotier-tools.tests;

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
