{ lib, ... }:
{
  clan.modules = {
    borgbackup = lib.modules.importApply ./default.nix { };
  };
}
