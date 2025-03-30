# Generate partial NixOS configurations for every machine in the inventory
# This function is responsible for generating the module configuration for every machine in the inventory.
{ lib, clanLib }:
let
  /*
    Returns a set with NixOS configuration for every machine in the inventory.

    machinesFromInventory :: Inventory -> { ${machine_name} :: NixOSConfiguration }
  */
  buildInventory =
    { inventory, directory }:
    (lib.evalModules {
      specialArgs = {
        inherit clanLib;
      };
      modules = [
        ./builder
        { inherit directory inventory; }
      ];
    }).config;
in
{
  inherit buildInventory;
}
