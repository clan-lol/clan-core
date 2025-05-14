{ lib, ... }:
{
  clan.modules = {
    admin = lib.modules.importApply ./default.nix { };
  };
}
