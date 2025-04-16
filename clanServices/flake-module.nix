{ self, lib, ... }:
{
  clan.inventory.modules = {
    zerotier-redux = lib.modules.importApply ./zerotier-redux/default.nix {
      inherit (self) packages;
    };
  };
}
