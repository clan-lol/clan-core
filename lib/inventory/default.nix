{ lib, clan-core }:
{
  buildInventory = import ./build-inventory { inherit lib clan-core; };
  interface = ./build-inventory/interface.nix;
}
