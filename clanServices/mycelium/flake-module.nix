{ lib, self, ... }:
{
  clan.modules = {
    mycelium = lib.modules.importApply ./default.nix { };
  };
  perSystem =
    { pkgs, ... }:
    {
      checks = lib.optionalAttrs (pkgs.stdenv.isLinux) {
        mycelium = import ./tests/vm/default.nix {
          inherit pkgs;
          clan-core = self;
          nixosLib = import (self.inputs.nixpkgs + "/nixos/lib") { };
        };
      };
    };
}
