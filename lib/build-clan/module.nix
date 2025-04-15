{
  config,
  clan-core,
  nixpkgs,
  nix-darwin,
  lib,
  ...
}:
let
  inherit (config)
    directory
    pkgsForSystem
    specialArgs
    inventory
    ;

  inherit (clan-core.clanLib.inventory) buildInventory;

  supportedSystems = [
    "x86_64-linux"
    "aarch64-linux"
    "riscv64-linux"
    "x86_64-darwin"
    "aarch64-darwin"
  ];

  /*
    An attrset with nixpkgs instantiated for each platform.
    This is important, as:
      1. We don't want to call `pkgsForSystem system` multiple times
      2. We need to fall back to `nixpkgs.legacyPackages.${system}` in case pkgsForSystem returns null
  */
  pkgsFor = lib.genAttrs supportedSystems (
    system:
    let
      pkgs = pkgsForSystem system;
    in
    if pkgs != null then pkgs else nixpkgs.legacyPackages.${system}
  );

  # map from machine name to service configuration
  # { ${machineName} :: Config }
  inventoryClass = (
    buildInventory {
      inherit inventory directory;
      flakeInputs = config.self.inputs;
    }
  );

  moduleSystemConstructor = {
    # TODO: remove default system once we have a hardware-config mechanism
    nixos =
      {
        system ? null,
        name,
        pkgs ? null,
      }:
      nixpkgs.lib.nixosSystem {
        modules =
          let
            innerModule = lib.modules.importApply ./machineModules/forSystem.nix {
              inherit
                pkgs
                pkgsForSystem
                system
                ;
            };
            staticModules = (
              lib.modules.importApply ./machineModules/forName.nix {
                inherit
                  name
                  directory
                  ;
              }
            );
          in
          [
            (config.outputs.moduleForMachine.${name} or { })
            staticModules
            innerModule
            {
              config.clan.core.module = innerModule;
            }
          ];

        specialArgs = {
          inherit clan-core;
        } // specialArgs;
      };

    darwin =
      {
        system ? null,
        name,
        pkgs ? null,
      }:
      nix-darwin.lib.darwinSystem {
        modules = [
          (config.outputs.moduleForMachine.${name} or { })
          # We split the modules to reduce the number of dependencies
          # This module only depends on the machine name
          # and the directory
          (lib.modules.importApply ./machineModules/forName.nix {
            inherit
              name
              directory
              ;
          })
          # This module depends on the system and pkgs
          # It contains optional logic to override 'nixpkgs.pkgs' and 'nixpkgs.hostPlatform'
          # and other 'system' related logic
          (lib.modules.importApply ./machineModules/forSystem.nix {
            inherit
              pkgs
              pkgsForSystem
              system
              ;
          })
        ];

        specialArgs = {
          inherit clan-core;
        } // specialArgs;
      };
  };

  allMachines = inventoryClass.machines; # <- inventory.machines <- clan.machines

  machineClasses = lib.mapAttrs (
    name: _: inventory.machines.${name}.machineClass or "nixos"
  ) allMachines;

  configurations = lib.mapAttrs (
    name: _: moduleSystemConstructor.${machineClasses.${name}} { inherit name; }
  ) allMachines;

  nixosConfigurations = lib.filterAttrs (name: _: machineClasses.${name} == "nixos") configurations;
  darwinConfigurations = lib.filterAttrs (name: _: machineClasses.${name} == "darwin") configurations;

  # This instantiates NixOS for each system that we support:
  # configPerSystem = <system>.<machine>.nixosConfiguration
  # We need this to build nixos secret generators for each system
  configsPerSystem = builtins.listToAttrs (
    builtins.map (
      system:
      lib.nameValuePair system (
        lib.mapAttrs (
          name: _:
          moduleSystemConstructor.${machineClasses.${name}} {
            inherit name system;
            pkgs = pkgsFor.${system};
          }
        ) allMachines
      )
    ) supportedSystems
  );

  inventoryFile = "${directory}/inventory.json";

  inventoryLoaded =
    if builtins.pathExists inventoryFile then
      (builtins.fromJSON (builtins.readFile inventoryFile))
    else
      { };

in
{
  imports = [
    {
      options.outputs.moduleForMachine = lib.mkOption {
        type = lib.types.attrsOf (
          lib.types.deferredModuleWith {
            staticModules = [
              (
                { _class, ... }:
                {
                  imports = lib.optionals (_class == "nixos") [
                    clan-core.nixosModules.clanCore
                  ];
                }
              )
            ];
          }
        );
      };
      config.outputs.moduleForMachine = lib.mkMerge [
        # Create one empty module for each machine such that there is a default for each machine
        # See: 'staticModules' in the moduleForMachine option
        # This is only necessary because clan.machines doesn't include all machines
        # There can other sources: i.e. inventory
        (lib.mapAttrs (
          name: v:
          (
            { _class, ... }:
            {
              imports = (v.machineImports or [ ]);
              config = lib.optionalAttrs (_class == "nixos") {
                clan.core.settings = {
                  inherit (config.inventory.meta) name icon;

                  inherit directory;
                  machine = {
                    inherit name;
                  };
                };
              };

            }
          )
        ) inventoryClass.machines)

        # The user can define some machine config here
        # i.e. 'clan.machines.jon = ...'
        config.machines
      ];
    }
    # Merge the inventory file
    {
      inventory = _: {
        _file = inventoryFile;
        config = inventoryLoaded;
      };
    }
    # TODO: Figure out why this causes infinite recursion
    {
      inventory.machines = lib.optionalAttrs (builtins.pathExists "${directory}/machines") (
        builtins.mapAttrs (_n: _v: { }) (
          lib.filterAttrs (_: t: t == "directory") (builtins.readDir "${directory}/machines")
        )
      );
    }
    {
      inventory.machines = lib.mapAttrs (_n: _: { }) config.machines;
    }
    # Merge the meta attributes from the buildClan function
    {
      inventory.modules = clan-core.clanModules;
    }
    # config.inventory.meta <- config.meta
    { inventory.meta = config.meta; }
    # Set default for computed tags
    ./computed-tags.nix
  ];

  inherit nixosConfigurations;
  inherit darwinConfigurations;

  clanInternals = {
    moduleSchemas = clan-core.clanLib.modules.getModulesSchema {
      modules = config.inventory.modules;
      # TODO: make this function system agnostic
      pkgs = nixpkgs.legacyPackages."x86_64-linux";
      inherit clan-core;
    };
    inherit inventoryClass;

    # TODO: unify this interface
    # We should have only clan.modules. (consistent with clan.templates)
    inherit (clan-core) clanModules clanLib;
    modules = config.modules;

    inherit inventoryFile;
    inventoryValuesPrios =
      # Temporary workaround
      builtins.removeAttrs (clan-core.clanLib.values.getPrios { options = inventory.options; })
        # tags are freeformType which is not supported yet.
        [ "tags" ];

    templates = config.templates;
    inventory = config.inventory;
    meta = config.inventory.meta;

    source = "${clan-core}";

    # machine specifics
    machines = configsPerSystem;
    all-machines-json =
      if !lib.hasAttrByPath [ "darwinModules" "clanCore" ] clan-core then
        lib.mapAttrs (
          system: configs:
          nixpkgs.legacyPackages.${system}.writers.writeJSON "machines.json" (
            lib.mapAttrs (_: m: m.config.system.clan.deployment.data) (
              lib.filterAttrs (_n: v: v.class == "nixos") configs
            )
          )
        ) configsPerSystem
      else
        throw "remove NixOS filter and support nix-darwin as well";
  };
}
