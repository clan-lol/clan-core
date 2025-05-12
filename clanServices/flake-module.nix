{ lib, ... }:
{
  imports = [
    ./hello-world/flake-module.nix
  ];

  clan.modules = {
    admin = lib.modules.importApply ./admin/default.nix { };
  };
}
