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
  clan.modules = {
    zerotier = module;
  };
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
      # zerotier = import ./tests/vm/default.nix {
      #   inherit module;
      #   inherit inputs pkgs;
      #   clan-core = self;
      #   nixosLib = import (self.inputs.nixpkgs + "/nixos/lib") { };
      # };
    };
}
