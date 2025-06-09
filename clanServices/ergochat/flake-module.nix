{ lib, self, ... }:
{
  clan.modules = {
    ergochat = lib.modules.importApply ./default.nix { };
  };
  perSystem =
    { pkgs, ... }:
    {
      checks = lib.optionalAttrs (pkgs.stdenv.isLinux) {
        ergochat = import ./tests/vm/default.nix {
          inherit pkgs;
          clan-core = self;
          nixosLib = import (self.inputs.nixpkgs + "/nixos/lib") { };
        };
      };
    };
}
