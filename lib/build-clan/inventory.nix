# Generate partial NixOS configurations for every machine in the inventory
# This function is responsible for generating the module configuration for every machine in the inventory.
{ lib, clan-core }:
inventory:
let
  machines = machinesFromInventory inventory;

  resolveTags =
    # Inventory, { machines :: [string], tags :: [string] }
    inventory: members: {
      machines =
        members.machines or [ ]
        ++ (builtins.foldl' (
          acc: tag:
          let
            tagMembers = builtins.attrNames (
              lib.filterAttrs (_n: v: builtins.elem tag v.tags or [ ]) inventory.machines
            );
          in
          # throw "Machine tag ${tag} not found. Not machine with: tag ${tagName} not in inventory.";
          if tagMembers == [ ] then
            throw "Machine tag ${tag} not found. Not machine with: tag ${tag} not in inventory."
          else
            acc ++ tagMembers
        ) [ ] members.tags or [ ]);
    };

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
              _roleName: members: resolveTags inventory members
            ) serviceConfig.roles;

            isInService = builtins.any (members: builtins.elem machineName members.machines) (
              builtins.attrValues resolvedRoles
            );

            # Inverse map of roles. Allows for easy lookup of roles for a given machine.
            # { ${machine_name} :: [roles]
            inverseRoles = lib.foldlAttrs (
              acc: roleName:
              { machines }:
              acc
              // builtins.foldl' (
                acc2: machineName: acc2 // { ${machineName} = (acc.${machineName} or [ ]) ++ [ roleName ]; }
              ) { } machines
            ) { } resolvedRoles;

            machineServiceConfig = (serviceConfig.machines.${machineName} or { }).config or { };
            globalConfig = serviceConfig.config or { };

            # TODO: maybe optimize this dont lookup the role in inverse roles. Imports are not lazy
            roleModules = builtins.map (
              role:
              let
                path = "${clan-core.clanModules.${moduleName}}/roles/${role}.nix";
              in
              if builtins.pathExists path then
                path
              else
                throw "Role doesnt have a module: ${role}. Path: ${path} not found."
            ) inverseRoles.${machineName} or [ ];
          in
          if isInService then
            acc2
            ++ [
              {
                imports = [ clan-core.clanModules.${moduleName} ] ++ roleModules;
                config.clan.${moduleName} = lib.mkMerge [
                  globalConfig
                  machineServiceConfig
                ];
              }
              {
                config.clan.inventory.services.${moduleName}.${instanceName} = {
                  roles = resolvedRoles;
                  # TODO: Add inverseRoles to the service config if needed
                  # inherit inverseRoles;
                };
              }
            ]
          else
            acc2
        ) [ ] serviceConfigs)
      ) [ ] inventory.services
    ) inventory.machines;
in
machines
