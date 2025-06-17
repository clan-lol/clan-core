{
  lib,
  self,
  inputs,
  ...
}:
let
  module = lib.modules.importApply ./default.nix { };
in
{
  clan.modules.zerotier = module;
  perSystem =
    { ... }:
    let
      unit-test-module = (
        self.clanLib.test.flakeModules.makeEvalChecks {
          inherit module;
          inherit self inputs;
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
    };
}
