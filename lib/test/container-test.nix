test:
{ pkgs, self, ... }:
let
  inherit (pkgs) lib;
  nixos-lib = import (pkgs.path + "/nixos/lib") { };
in
(nixos-lib.runTest {
  hostPkgs = pkgs;
  # speed-up evaluation
  defaults =
    { config, options, ... }:
    {
      imports = [
        self.clanLib.test.minifyModule
      ];
      config = lib.optionalAttrs (options ? clan) {
        clan.core.settings.machine.name = config.networking.hostName;
      };
    };
  # TODO: Remove this. We should not pass special args in the test framework
  # Instead each test can forward the special args it needs
  # to accept external dependencies such as disko
  node.specialArgs.self = self;
  _module.args = { inherit self; };

  imports = [
    test
    ./container-test-driver/driver-module.nix
  ];
}).config.result
