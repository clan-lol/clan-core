{ self, lib, ... }:
let
  clan-core = self;

  # syncthing_inventory = builtins.fromJSON (builtins.readFile ./src/tests/syncthing.json);
  syncthing_inventory = builtins.fromJSON (builtins.readFile ./src/tests/borgbackup.json);

  machines = machinesFromInventory syncthing_inventory;

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
            globalConfig = serviceConfig.config;

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
                config.clan.inventory.${moduleName}.${instanceName} = {
                  roles = resolvedRoles;
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
{
  inherit clan-core;

  new_clan = clan-core.lib.buildInventory {
    # High level services.
    # If you need multiple instances of a service configure them via:
    # inventory.services.[serviceName].[instanceName] = ...
    services = {
      borbackup = {
        roles.server.machines = [ "vyr" ];
        roles.client.tags = [ "laptop" ];
        machines.vyr = {
          config = {

          };
        };
        config = {

        };
      };
    };

    # Low level inventory i.e. if you need multiple instances of a service
    # Or if you want to manipulate the created inventory directly.
    inventory.services.borbackup.default = { };

    # Machines. each machine can be referenced by its attribute name under services.
    machines = {
      camina = {
        # This is added to machine tags
        clan.tags = [ "laptop" ];
        # These are the inventory machine fields
        clan.meta.description = "";
        clan.meta.name = "";
        clan.meta.icon = "";
        # Config ...
      };
      vyr = {
        # Config ...
      };
      vi = {
        clan.networking.targetHost = "root@78.47.164.46";
        # Config ...
      };
      aya = {
        clan.networking.targetHost = "root@78.47.164.46";
        # Config ...
      };
      ezra = {
        # Config ...
      };
      rianon = {
        # Config ...
      };
    };
  };

  clan = clan-core.lib.buildClan {
    meta.name = "vi's clans";
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
