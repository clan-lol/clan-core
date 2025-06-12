{ lib, ... }:
{
  clan.modules = {
    emergency-access = lib.modules.importApply ./default.nix { };
  };
}
