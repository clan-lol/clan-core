test:
{ pkgs, self, ... }:
let
  inherit (pkgs) lib;
  nixos-lib = import (pkgs.path + "/nixos/lib") { };
  # Use patched nix for container tests to handle overlay filesystem chmod issues
  hostPkgs = pkgs.extend (
    _final: _prev: {
      nix = self.packages.${pkgs.stdenv.hostPlatform.system}.nix;
    }
  );
in
(nixos-lib.runTest {
  inherit hostPkgs;
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
