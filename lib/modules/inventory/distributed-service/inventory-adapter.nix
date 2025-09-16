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
  clanLib,
  ...
}:
{
  mapInstances =
    {
      # This is used to resolve the module imports from 'flake.inputs'
      flakeInputs,
      # The clan inventory
      inventory,
      directory,
      clanCoreModules,
      prefix ? [ ],
      exportsModule,
    }:
    let
      # machineHasTag = machineName: tagName: lib.elem tagName inventory.machines.${machineName}.tags;

      # map the instances into the module
      importedModuleWithInstances = lib.mapAttrs (
        instanceName: instance:
        let
          resolvedModule = clanLib.resolveModule {
            moduleSpec = instance.module;
            inherit flakeInputs clanCoreModules;
          };

          # Every instance includes machines via roles
          # :: { client :: ... }
          instanceRoles = lib.mapAttrs (
            roleName: role:
            let
              resolvedMachines = clanLib.inventory.resolveTags {
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
            # Remove "tags", they are resolved into "machines"
            (removeAttrs role [ "tags" ])
            // {
              machines = lib.genAttrs resolvedMachines.machines (
                machineName:
                let
                  machineSettings = instance.roles.${roleName}.machines.${machineName}.settings or { };
                in
                # TODO: tag settings
                # Wait for this feature until option introspection for 'settings' is done.
                # This might get too complex to handle otherwise.
                # settingsViaTags = lib.filterAttrs (
                #   tagName: _: machineHasTag machineName tagName
                # ) instance.roles.${roleName}.tags;
                {
                  # TODO: Do we want to wrap settings with
                  # setDefaultModuleLocation "inventory.instances.${instanceName}.roles.${roleName}.tags.${tagName}";
                  settings = {
                    imports = [
                      machineSettings
                    ]; # ++ lib.attrValues (lib.mapAttrs (_tagName: v: v.settings) settingsViaTags);
                  };
                }
              );
            }
          ) instance.roles;
        in
        {
          inherit (instance) module;
          inherit resolvedModule instanceRoles;
        }
      ) inventory.instances or { };

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

      # servicesEval.config.mappedServices.self-A.result.final.jon.nixosModule
      allMachines = lib.mapAttrs (machineName: _: {
        # This is the list of nixosModules for each machine
        machineImports = lib.foldlAttrs (
          acc: _module_ident: serviceModule:
          acc ++ [ serviceModule.result.final.${machineName}.nixosModule or { } ]
        ) [ ] servicesEval.config.mappedServices;
      }) inventory.machines or { };

      evalServices =
        { modules, prefix }:
        lib.evalModules {
          class = "clan";
          specialArgs = {
            inherit clanLib;
            _ctx = prefix;
          };
          modules = [
            (import ./all-services-wrapper.nix { inherit directory; })
          ]
          ++ modules;
        };

      servicesEval = evalServices {
        inherit prefix;
        modules = [
          {
            inherit exportsModule;
            mappedServices = lib.mapAttrs (_module_ident: instances: {
              imports = [
                # Import the resolved module.
                # i.e. clan.modules.admin
                (builtins.head instances).instance.resolvedModule
              ] # Include all the instances that correlate to the resolved module
              ++ (builtins.map (v: {
                instances.${v.instanceName}.roles = v.instance.instanceRoles;
              }) instances);
            }) grouped;
          }
        ];
      };
      importedModulesEvaluated = servicesEval.config.mappedServices;

    in
    {
      inherit
        servicesEval
        importedModuleWithInstances
        grouped
        allMachines
        importedModulesEvaluated
        ;
    };
}
