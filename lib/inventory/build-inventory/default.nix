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
      prefix ? [ ],
      localModuleSet ? { },
    }:
    (lib.evalModules {
      # TODO: remove clanLib from specialArgs
      specialArgs = {
        inherit clanLib;
      };
      modules = [
        ./builder
        (lib.modules.importApply ./service-list-from-inputs.nix {
          inherit flakeInputs clanLib localModuleSet;
        })
        { inherit directory inventory; }
        (
          # config.distributedServices.allMachines.${name} or [ ];
          { config, ... }:
          {

            distributedServices = clanLib.inventory.mapInstances {
              inherit (config) inventory;
              inherit flakeInputs;
              prefix = prefix ++ [ "distributedServices" ];
            };
            machines = lib.mapAttrs (_machineName: v: {
              machineImports = v;
            }) config.distributedServices.allMachines;

          }
        )
        (lib.modules.importApply ./inventory-introspection.nix { inherit clanLib; })
      ];
    }).config;
in
{
  inherit buildInventory;
}
