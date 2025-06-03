{ lib, ... }:
{
  clan.modules = {
    ergochat = lib.modules.importApply ./default.nix { };
  };
}
