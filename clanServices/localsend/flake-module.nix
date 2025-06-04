{ lib, ... }:
{
  clan.modules = {
    localsend = lib.modules.importApply ./default.nix { };
  };
}
