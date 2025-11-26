{
  lib,
  clanLib,
  config,
  clan-core,
  ...
}:
let
  inherit (lib) mkOption types;
  # Keep a reference to top-level
  clanConfig = config;

  inventory = clanConfig.inventory;
  flakeInputs = clanConfig.self.inputs;
  clanCoreModules = clan-core.clan.modules;

  grouped = lib.foldlAttrs (
    acc: instanceName: instance:
    let
      inputName = if instance.module.input == null then "<clan-core>" else instance.module.input;
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
in
{
  _class = "clan";
  options._services = mkOption {
    visible = false;
    description = ''
      All service instances

      !!! Danger "Internal API"
        Do not rely on this API yet.

        - Will be renamed to just 'services' in the future.
        Once the name can be claimed again.
        - Structure will change.

        API will be declared as public after beeing simplified.
    '';
    type = types.submoduleWith {
      # TODO: Remove specialArgs
      specialArgs = {
        inherit clanLib;
      };
      modules = [
        (import ../../lib/inventory/distributed-service/all-services-wrapper.nix {
          inherit (clanConfig) directory exports;
        })
        # Dependencies
        {
          # exportsModule = clanConfig.exportsModule;
        }
        {
          # TODO: Rename to "allServices"
          # All services
          mappedServices = lib.mapAttrs (_module_ident: instances: {
            imports = [
              # Import the resolved module.
              # i.e. clan.modules.admin
              {
                options.module = lib.mkOption {
                  type = lib.types.raw;
                  default = (builtins.head instances).instance.module;
                };
              }
              (builtins.head instances).instance.resolvedModule
            ] # Include all the instances that correlate to the resolved module
            ++ (builtins.map (v: {
              instances.${v.instanceName}.roles = v.instance.instanceRoles;
            }) instances);
          }) grouped;
        }
      ];
    };
    default = { };
  };
  options._allMachines = mkOption {
    internal = true;
    type = types.raw;
    default = lib.mapAttrs (machineName: _: {
      # This is the list of nixosModules for each machine
      machineImports = lib.foldlAttrs (
        acc: _module_ident: serviceModule:
        acc ++ [ serviceModule.result.final.${machineName}.nixosModule or { } ]
      ) [ ] config._services.mappedServices;
    }) inventory.machines or { };
  };

  config = {
    clanInternals.inventoryClass.machines = config._allMachines;
    # clanInternals.inventoryClass.distributedServices = config._services;

    # Exports from distributed services
    exports = config._services.exports;
  };
}
