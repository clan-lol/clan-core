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
      # TODO: move clanLib from specialArgs to options
      specialArgs = {
        inherit clanLib;
      };
      modules = [
        ./builder/default.nix
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
              inherit localModuleSet;
              inherit flakeInputs;
              prefix = prefix ++ [ "distributedServices" ];
            };
            machines = config.distributedServices.allMachines;

          }
        )
        ./inventory-introspection.nix
      ];
    }).config;
in
{
  inherit buildInventory;
}
