{ lib, ... }:
{
  clan.modules = {
    heisenbridge = lib.modules.importApply ./default.nix { };
  };
}
