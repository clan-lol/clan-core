{ lib, ... }:
{
  clan.modules = {
    deltachat = lib.modules.importApply ./default.nix { };
  };
}