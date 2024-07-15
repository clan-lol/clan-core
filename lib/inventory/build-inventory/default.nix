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
            # For error printing
            availableTags = lib.foldlAttrs (
              acc: _: v:
              v.tags or [ ] ++ acc
            ) [ ] inventory.machines;

            tagMembers = builtins.attrNames (
              lib.filterAttrs (_n: v: builtins.elem tag v.tags or [ ]) inventory.machines
            );
          in
          if tagMembers == [ ] then
            throw "Tag: '${tag}' not found. Available tags: ${builtins.toJSON (lib.unique availableTags)}"
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
      machineName: machineConfig:
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
                throw "Module doesn't have role: '${role}'. Path: ${path} not found."
            ) inverseRoles.${machineName} or [ ];

            roleServiceConfigs = builtins.map (
              role: serviceConfig.roles.${role}.config or { }
            ) inverseRoles.${machineName} or [ ];
          in
          if isInService then
            acc2
            ++ [
              {
                imports = [ clan-core.clanModules.${moduleName} ] ++ roleModules;
                config.clan.${moduleName} = lib.mkMerge (
                  [
                    globalConfig
                    machineServiceConfig
                  ]
                  ++ roleServiceConfigs
                );
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
      # Append each machine config
      ++ [
        (lib.optionalAttrs (machineConfig.system or null != null) {
          config.nixpkgs.hostPlatform = machineConfig.system;
        })
      ]
    ) inventory.machines or { };
in
machines
