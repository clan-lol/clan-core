{ lib, ... }:
{
  imports = [
    ./hello-world/flake-module.nix
  ];

  clan.inventory.modules = {
    admin = lib.modules.importApply ./admin/default.nix {
      # inherit (self) packages;
    };
  };

}
