{ lib, ... }:
{
  clan.modules = {
    garage = lib.modules.importApply ./default.nix { };
  };
}
