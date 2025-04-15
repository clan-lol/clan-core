test:
{ pkgs, self, ... }:
let
  inherit (pkgs) lib;
  nixos-lib = import (pkgs.path + "/nixos/lib") { };
in
(nixos-lib.runTest {
  hostPkgs = pkgs;
  # speed-up evaluation
  defaults = (
    { config, options, ... }:
    {
      imports = [
        self.clanLib.test.minifyModule
      ];
      config = lib.mkMerge [
        (lib.optionalAttrs (options ? clan) {
          clan.core.settings.machine.name = config.networking.hostName;
        })
        {
          documentation.enable = lib.mkDefault false;
          nix.settings.min-free = 0;
          system.stateVersion = config.system.nixos.release;
        }
      ];
    }
  );

  _module.args = { inherit self; };
  # to accept external dependencies such as disko
  node.specialArgs.self = self;
  imports = [ test ];
}).config.result
