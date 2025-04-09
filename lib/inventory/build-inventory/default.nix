# Generate partial NixOS configurations for every machine in the inventory
# This function is responsible for generating the module configuration for every machine in the inventory.
{ lib, clanLib }:
let
  /*
    Returns a set with NixOS configuration for every machine in the inventory.

    machinesFromInventory :: Inventory -> { ${machine_name} :: NixOSConfiguration }
  */
  buildInventory =
    {
      inventory,
      directory,
      flakeInputs,
    }:
    (lib.evalModules {
      specialArgs = {
        inherit clanLib;
      };
      modules = [
        ./builder
        { inherit directory inventory; }
        (
          # config.distributedServices.allMachines.${name} or [ ];
          { config, ... }:
          {
            distributedServices = clanLib.inventory.mapInstances {
              inherit (config) inventory;
              inherit flakeInputs;
            };
            machines = lib.mapAttrs (_machineName: v: {
              machineImports = v;
            }) config.distributedServices.allMachines;
          }
        )
      ];
    }).config;
in
{
  inherit buildInventory;
}
