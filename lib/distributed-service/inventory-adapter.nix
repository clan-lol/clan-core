# Adapter function between the inventory.instances and the clan.service module
#
# Data flow:
# - inventory.instances -> Adapter -> clan.service module -> Service Resources (i.e. NixosModules per Machine, Vars per Service, etc.)
#
# What this file does:
#
# - Resolves the [Module] to an actual module-path and imports it.
# - Groups together all the same modules into a single import and creates all instances for it.
# - Resolves the inventory tags into machines. Tags don't exist at the service level.
#   Also combines the settings for 'machines' and 'tags'.
{
  lib,
  # This is used to resolve the module imports from 'flake.inputs'
  flake,
  # The clan inventory
  inventory,
}:
let
  # Returns the list of machine names
  # { ... } -> [ string ]
  resolveTags =
    {
      # Available InventoryMachines :: { {name} :: { tags = [ string ]; }; }
      machines,
      # Requested members :: { machines, tags }
      # Those will be resolved against the available machines
      members,
      # Not needed for resolution - only for error reporting
      roleName,
      instanceName,
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
            ) [ ] (machines);

            tagMembers = builtins.attrNames (lib.filterAttrs (_n: v: builtins.elem tag v.tags or [ ]) machines);
          in
          if tagMembers == [ ] then
            lib.warn ''
              Service instance '${instanceName}': - ${roleName} tags: no machine with tag '${tag}' found.
              Available tags: ${builtins.toJSON (lib.unique availableTags)}
            '' acc
          else
            acc ++ tagMembers
        ) [ ] members.tags or [ ]);
    };

  machineHasTag = machineName: tagName: lib.elem tagName inventory.machines.${machineName}.tags;

  # map the instances into the module
  importedModuleWithInstances = lib.mapAttrs (
    instanceName: instance:
    let
      # TODO:
      resolvedModuleSet =
        # If the module.name is self then take the modules defined in the flake
        # Otherwise its an external input which provides the modules via 'clan.modules' attribute
        if instance.module.input == null then
          inventory.modules
        else
          let
            input =
              flake.inputs.${instance.module.input} or (throw ''
                Flake doesn't provide input with name '${instance.module.input}'

                Choose one of the following inputs:
                - ${
                  builtins.concatStringsSep "\n- " (
                    lib.attrNames (lib.filterAttrs (name: input: input ? clan) flake.inputs)
                  )
                }

                To import a local module from 'inventory.modules' remove the 'input' attribute from the module definition
                Remove the following line from the module definition:

                ...
                - module.input = "${instance.module.input}"


              '');
            clanAttrs =
              input.clan
                or (throw "It seems the flake input ${instance.module.input} doesn't export any clan resources");
          in
          clanAttrs.modules;

      resolvedModule =
        resolvedModuleSet.${instance.module.name}
          or (throw "flake doesn't provide clan-module with name ${instance.module.name}");

      # Every instance includes machines via roles
      # :: { client :: ... }
      instanceRoles = lib.mapAttrs (
        roleName: role:
        let
          resolvedMachines = resolveTags {
            members = {
              # Explicit members
              machines = lib.attrNames role.machines;
              # Resolved Members
              tags = lib.attrNames role.tags;
            };
            inherit (inventory) machines;
            inherit instanceName roleName;
          };
        in
        # instances.<instanceName>.roles.<roleName> =
        {
          machines = lib.genAttrs resolvedMachines.machines (
            machineName:
            let
              machineSettings = instance.roles.${roleName}.machines.${machineName}.settings or { };
              settingsViaTags = lib.filterAttrs (
                tagName: _: machineHasTag machineName tagName
              ) instance.roles.${roleName}.tags;
            in
            {
              # TODO: Do we want to wrap settings with
              # setDefaultModuleLocation "inventory.instances.${instanceName}.roles.${roleName}.tags.${tagName}";
              settings = {
                imports = [
                  machineSettings
                ] ++ lib.attrValues (lib.mapAttrs (tagName: v: v.settings) settingsViaTags);
              };
            }
          );
          # Maps to settings for the role.
          # In other words this sets the following path of a clan.service module:
          # instances.<instanceName>.roles.<roleName>.settings
          settings = role.settings;
        }
      ) instance.roles;
    in
    {
      inherit (instance) module;
      inherit resolvedModule instanceRoles;
    }
  ) inventory.instances;

  # TODO: Eagerly check the _class of the resolved module
  evals = lib.mapAttrs (
    _module_ident: instances:
    (lib.evalModules {
      class = "clan.service";
      modules =
        [
          # Import the resolved module
          (builtins.head instances).instance.resolvedModule
        ]
        # Include all the instances that correlate to the resolved module
        ++ (builtins.map (v: {
          instances.${v.instanceName}.roles = v.instance.instanceRoles;
        }) instances);
    })
  ) grouped;

  # Group the instances by the module they resolve to
  # This is necessary to evaluate the module in a single pass
  # :: { <module.input>_<module.name> :: [ { name, value } ] }
  # Since 'perMachine' needs access to all the instances we should include them as a whole
  grouped = lib.foldlAttrs (
    acc: instanceName: instance:
    let
      inputName = if instance.module.input == null then "self" else instance.module.input;
      id = inputName + "-" + instance.module.name;
    in
    acc
    // {
      ${id} = acc.${id} or [ ] ++ [
        {
          inherit instanceName instance;
        }
      ];
    }
  ) { } importedModuleWithInstances;
in
{
  inherit importedModuleWithInstances grouped;
  inherit evals;
}
