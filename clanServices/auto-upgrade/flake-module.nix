{ lib, ... }:
{
  clan.modules = {
    auto-upgrade = lib.modules.importApply ./default.nix { };
  };
}
