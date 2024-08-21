{ lib, clan-core }:
{
  inherit (import ./build-inventory { inherit lib clan-core; }) buildInventory;
  interface = ./build-inventory/interface.nix;
}
