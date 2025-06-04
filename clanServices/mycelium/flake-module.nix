{ lib, ... }:
{
  clan.modules = {
    mycelium = lib.modules.importApply ./default.nix { };
  };
}
