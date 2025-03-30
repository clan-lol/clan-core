{ lib, clanLib }:
{
  inherit (import ./build-inventory { inherit lib clanLib; }) buildInventory;
  interface = ./build-inventory/interface.nix;
}
