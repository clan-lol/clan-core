{ lib, ... }:
{
  clan.modules = {
    importer = lib.modules.importApply ./default.nix { };
  };
}
