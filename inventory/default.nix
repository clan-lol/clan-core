{ inputs, self, ... }:
let
  clan-core = self;
  system = "x86_64-linux";
  pkgs = clan-core.inputs.nixpkgs.legacyPackages.${system};

  # syncthing_inventory = builtins.fromJSON (builtins.readFile ./src/tests/syncthing.json);
  syncthing_inventory = builtins.fromJSON (builtins.readFile ./src/tests/borgbackup.json);

  machines = machinesFromInventory {
    inherit clan-core;
    lib = pkgs.lib;
  } syncthing_inventory;

  /*
    Returns a NixOS configuration for every machine in the inventory.

    machinesFromInventory :: Inventory -> { ${machine_name} :: NixOSConfiguration }
  */
  machinesFromInventory =
    { lib, clan-core, ... }:
    inventory:
    # For every machine in the inventory, build a NixOS configuration
    # For each machine generate config, forEach service, if the machine is used.
    builtins.mapAttrs (
      machine_name: _:
      builtins.foldl' (
        acc: service_name:
        let
          service_config = inventory.services.${service_name};
          isInService = builtins.elem machine_name (builtins.attrNames service_config.machineConfig);

          machine_service_config = (service_config.machineConfig.${machine_name} or { }).config or { };
          global_config = inventory.services.${service_name}.config;
          module_name = inventory.services.${service_name}.module;
        in
        # Possible roles: "server", "client", "peer"
        if
          builtins.trace ''
            isInService ${builtins.toJSON isInService},
            ${builtins.toJSON machine_name} ${builtins.toJSON (builtins.attrNames service_config.machineConfig)}
          '' isInService
        then
          acc
          ++ [
            {
              imports = [ clan-core.clanModules.${module_name} ];
              config.clan.${module_name} = lib.mkMerge [
                global_config
                machine_service_config
              ];
            }
            {
              config.clan.${module_name} = {
                # TODO: filter, show only the roles that are needed by the machine
                roles = builtins.mapAttrs (_m: c: c.roles) service_config.machineConfig;
              };
            }
          ]
        else
          acc
      ) [ ] (builtins.attrNames inventory.services)
    ) inventory.machines;
in
{
  clan = clan-core.lib.buildClan {
    meta.name = "vis clans";
    # Should usually point to the directory of flake.nix
    directory = self;

    machines = {
      "vi_machine" = {
        imports = machines.vi_machine;
      };
      "vyr_machine" = {
        imports = machines.vyr_machine;
      };
      "camina_machine" = {
        imports = machines.camina_machine;
      };
    };
  };
  intern = machines;
  # inherit (clan) nixosConfigurations clanInternals;
  # add the Clan cli tool to the dev shell
  devShells.${system}.default = pkgs.mkShell {
    packages = [ clan-core.packages.${system}.clan-cli ];
  };
}
