# Generate partial NixOS configurations for every machine in the inventory
# This function is responsible for generating the module configuration for every machine in the inventory.
{ lib, clan-core }:
let
  resolveTags =
    # Inventory, { machines :: [string], tags :: [string] }
    {
      serviceName,
      instanceName,
      roleName,
      inventory,
      members,
    }:
    {
      machines =
        members.machines or [ ]
        ++ (builtins.foldl' (
          acc: tag:
          let
            # For error printing
            availableTags = lib.foldlAttrs (
              acc: _: v:
              v.tags or [ ] ++ acc
            ) [ ] (inventory.machines);

            tagMembers = builtins.attrNames (
              lib.filterAttrs (_n: v: builtins.elem tag v.tags or [ ]) inventory.machines
            );
          in
          if tagMembers == [ ] then
            throw ''
              inventory.services.${serviceName}.${instanceName}: - ${roleName} tags: no machine with tag '${tag}' found.
              Available tags: ${builtins.toJSON (lib.unique availableTags)}
            ''
          else
            acc ++ tagMembers
        ) [ ] members.tags or [ ]);
    };

  checkService =
    serviceName:
    let
      frontmatter = clan-core.lib.modules.getFrontmatter serviceName;
    in
    if builtins.elem "inventory" frontmatter.features or [ ] then true else false;

  /*
    Returns a NixOS configuration for every machine in the inventory.

    machinesFromInventory :: Inventory -> { ${machine_name} :: NixOSConfiguration }
  */
  buildInventory =
    { inventory, directory }:
    # For every machine in the inventory, build a NixOS configuration
    # For each machine generate config, forEach service, if the machine is used.
    builtins.mapAttrs (
      machineName: machineConfig:
      lib.foldlAttrs (
        # [ Modules ], String, { ${instance_name} :: ServiceConfig }
        acc: serviceName: serviceConfigs:
        acc
        # Collect service config
        ++ (lib.foldlAttrs (
          # [ Modules ], String, ServiceConfig
          acc2: instanceName: serviceConfig:
          let
            resolvedRoles = builtins.mapAttrs (
              roleName: members:
              resolveTags {
                inherit
                  serviceName
                  instanceName
                  roleName
                  inventory
                  members
                  ;
              }
            ) serviceConfig.roles;

            isInService = builtins.any (members: builtins.elem machineName members.machines) (
              builtins.attrValues resolvedRoles
            );

            # all roles where the machine is present
            machineRoles = builtins.attrNames (
              lib.filterAttrs (_role: roleConfig: builtins.elem machineName roleConfig.machines) resolvedRoles
            );
            machineServiceConfig = (serviceConfig.machines.${machineName} or { }).config or { };
            globalConfig = serviceConfig.config or { };

            globalExtraModules = serviceConfig.extraModules or [ ];
            machineExtraModules = serviceConfig.machines.${machineName}.extraModules or [ ];
            roleServiceExtraModules = builtins.foldl' (
              acc: role: acc ++ serviceConfig.roles.${role}.extraModules or [ ]
            ) [ ] machineRoles;

            # TODO: maybe optimize this dont lookup the role in inverse roles. Imports are not lazy
            roleModules = builtins.map (
              role:
              let
                # Check the module exists
                module =
                  clan-core.clanModules.${serviceName}
                    or (throw "ClanModule not found: '${serviceName}'. Make sure the module is added in the 'clanModules' attribute of clan-core.");

                path = module + "/roles/${role}.nix";
              in
              if builtins.pathExists path then
                path
              else
                throw "Module doesn't have role: '${role}'. Role: ${role}.nix not found."
            ) machineRoles;

            roleServiceConfigs = builtins.filter (m: m != { }) (
              builtins.map (role: serviceConfig.roles.${role}.config or { }) machineRoles
            );

            extraModules = map (s: if builtins.typeOf s == "string" then "${directory}/${s}" else s) (
              globalExtraModules ++ machineExtraModules ++ roleServiceExtraModules
            );
          in

          if isInService then
            acc2
            ++ [
              {
                imports = roleModules ++ extraModules;
              }
              (lib.optionalAttrs (globalConfig != { } || machineServiceConfig != { } || roleServiceConfigs != [ ])
                {
                  config.clan.${serviceName} = lib.mkMerge (
                    [
                      globalConfig
                      machineServiceConfig
                    ]
                    ++ roleServiceConfigs
                  );
                }
              )

              {
                config.clan.inventory.services.${serviceName}.${instanceName} = {
                  roles = resolvedRoles;
                  # TODO: Add inverseRoles to the service config if needed
                  # inherit inverseRoles;
                };
              }
            ]
          else
            acc2
        ) [ ] (serviceConfigs))
      ) [ ] inventory.services
      # Append each machine config
      ++ [
        (lib.optionalAttrs (machineConfig.system or null != null) {
          config.nixpkgs.hostPlatform = machineConfig.system;
        })
        (lib.optionalAttrs (machineConfig.deploy.targetHost or null != null) {
          config.clan.core.networking.targetHost = machineConfig.deploy.targetHost;
        })
        {
          assertions = lib.foldlAttrs (
            acc: serviceName: _:
            acc
            ++ [
              {
                assertion = checkService serviceName;
                message = ''
                  Service ${serviceName} cannot be used in inventory. It does not declare the 'inventory' feature.


                          To allow it add the following to the beginning of the README.md of the module:

                            ---
                            ...

                            features = [ "inventory" ]
                            ---

                          Also make sure to test the module with the 'inventory' feature enabled.

                '';
              }
            ]
          ) [ ] inventory.services;
        }
      ]
    ) (inventory.machines or { });
in
{
  inherit buildInventory;
}
