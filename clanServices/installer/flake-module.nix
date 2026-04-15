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
    installer = module;
  };
  perSystem =
    { ... }:
    let
      unit-test-module = (
        self.clanLib.test.flakeModules.makeEvalChecks {
          inherit module;
          inherit inputs;
          fileset = lib.fileset.unions [
            ../../clanServices/installer
            ../../nixosModules
          ];
          testName = "installer";
          tests = ./tests/eval-tests.nix;
          testArgs = { };
        }
      );
    in
    {
      imports = [ unit-test-module ];
    };
}
