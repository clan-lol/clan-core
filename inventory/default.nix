{ self, lib, ... }:
let
  clan-core = self;

  # syncthing_inventory = builtins.fromJSON (builtins.readFile ./src/tests/syncthing.json);
  syncthing_inventory = builtins.fromJSON (builtins.readFile ./src/tests/borgbackup.json);

  machines = machinesFromInventory syncthing_inventory;

  resolveGroups =
    inventory: members:
    lib.unique (
      builtins.foldl' (
        acc: currMember:
        let
          groupName = builtins.substring 6 (builtins.stringLength currMember - 6) currMember;
          groupMembers =
            if inventory.groups.machines ? ${groupName} then
              inventory.groups.machines.${groupName}
            else
              throw "Machine group ${currMember} not found. Key: groups.machines.${groupName} not in inventory.";
        in
        if lib.hasPrefix "group:" currMember then (acc ++ groupMembers) else acc ++ [ currMember ]
      ) [ ] members
    );

  /*
    Returns a NixOS configuration for every machine in the inventory.

    machinesFromInventory :: Inventory -> { ${machine_name} :: NixOSConfiguration }
  */
  machinesFromInventory =
    inventory:
    # For every machine in the inventory, build a NixOS configuration
    # For each machine generate config, forEach service, if the machine is used.
    builtins.mapAttrs (
      machineName: _:
      lib.foldlAttrs (
        # [ Modules ], String, { ${instance_name} :: ServiceConfig }
        acc: moduleName: serviceConfigs:
        acc
        # Collect service config
        ++ (lib.foldlAttrs (
          # [ Modules ], String, ServiceConfig
          acc2: instanceName: serviceConfig:
          let
            resolvedRoles = builtins.mapAttrs (
              _roleName: members: resolveGroups inventory members
            ) serviceConfig.roles;

            isInService = builtins.any (members: builtins.elem machineName members) (
              builtins.attrValues resolvedRoles
            );

            machineServiceConfig = (serviceConfig.machines.${machineName} or { }).config or { };
            globalConfig = serviceConfig.config;
          in
          if isInService then
            acc2
            ++ [
              {
                imports = [ clan-core.clanModules.${moduleName} ];
                config.clan.${moduleName} = lib.mkMerge [
                  globalConfig
                  machineServiceConfig
                ];
              }
              {
                config.clan.inventory.${instanceName} = {
                  roles = resolvedRoles;
                };
              }
            ]
          else
            acc2
        ) [ ] serviceConfigs)
      ) [ ] inventory.services
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
}
