{
  config,
  clan-core,
  nixpkgs,
  nix-darwin,
  lib,
  ...
}:
let
  inherit (lib)
    flip
    mapAttrs'
    ;

  inherit (config)
    directory
    inventory
    pkgsForSystem
    specialArgs
    ;

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

  inherit (clan-core) clanLib;

  moduleSystemConstructor = {
    # TODO: remove default system once we have a hardware-config mechanism
    nixos = nixpkgs.lib.nixosSystem;
    darwin = nix-darwin.lib.darwinSystem;
  };

  allMachines = config.clanInternals.inventoryClass.machines; # <- inventory.machines <- clan.machines

  machineClasses = lib.mapAttrs (
    name: _: inventory.machines.${name}.machineClass or "nixos"
  ) allMachines;

  configurations = lib.mapAttrs (
    name: _:
    moduleSystemConstructor.${machineClasses.${name}} {
      # ATTENTION!: Dont add any modules here.
      # Add them to 'outputs.moduleForMachine.${name}' instead.
      modules = [ (config.outputs.moduleForMachine.${name} or { }) ];
      specialArgs = {
        inherit clan-core;
      } // specialArgs;
    }
  ) allMachines;

  # Expose reusable modules these can be imported or wrapped or instantiated
  # - by the user
  # - by some test frameworks
  # IMPORTANT!: It is utterly important that we don't add any logic outside of these modules, as it would get tested.
  nixosModules' = lib.filterAttrs (
    name: _: inventory.machines.${name}.machineClass or "nixos" == "nixos"
  ) (config.outputs.moduleForMachine);
  darwinModules' = lib.filterAttrs (
    name: _: inventory.machines.${name}.machineClass or "nixos" == "darwin"
  ) (config.outputs.moduleForMachine);

  nixosModules = flip mapAttrs' nixosModules' (
    name: machineModule: {
      name = "clan-machine-${name}";
      value = machineModule;
    }
  );

  darwinModules = flip mapAttrs' darwinModules' (
    name: machineModule: {
      name = "clan-machine-${name}";
      value = machineModule;
    }
  );

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
            modules = [
              (config.outputs.moduleForMachine.${name} or { })
              (lib.modules.importApply ../machineModules/overridePkgs.nix {
                pkgs = pkgsFor.${system};
              })
            ];
            specialArgs = {
              inherit clan-core;
            } // specialArgs;
          }
        ) allMachines
      )
    ) supportedSystems
  );

in
{
  imports = [
    (
      { ... }:
      let
        file = "${directory}/inventory.json";

        inventoryLoaded =
          if builtins.pathExists file then (builtins.fromJSON (builtins.readFile file)) else { };
      in
      {
        imports = [
          {
            inventory._inventoryFile = file;
          }
        ];
        # Weirdly this works only if it is a function
        # This seems to be a bug in nixpkgs
        inventory = _: lib.setDefaultModuleLocation file inventoryLoaded;
      }
    )
    {
      # TODO: Figure out why this causes infinite recursion
      inventory.machines = lib.optionalAttrs (builtins.pathExists "${directory}/machines") (
        builtins.mapAttrs (_n: _v: { }) (
          lib.filterAttrs (_: t: t == "directory") (builtins.readDir "${directory}/machines")
        )
      );
    }
    {
      inventory.machines = lib.mapAttrs (_n: _: { }) config.machines;
    }
    # config.inventory.meta <- config.meta
    # Set default for computed tags
    ./computed-tags.nix
  ];

  options.outputs.moduleForMachine = lib.mkOption {
    type = lib.types.attrsOf lib.types.deferredModule;
  };

  config = {
    inventory.modules = clan-core.clanModules;
    inventory._legacyModules = clan-core.clanModules;
    inventory.meta = config.meta;

    outputs.moduleForMachine = lib.mkMerge [
      # Create some modules for each machine
      # These can depend on the 'name' and
      # everything that can be derived from the machine 'name'
      # i.e. by looking up the corresponding information in the 'inventory' or 'clan' submodule
      (lib.mapAttrs (
        name: v:
        (
          { ... }@args:
          let
            _class =
              args._class or (throw ''
                Your version of nixpkgs is incompatible with the latest clan.
                Please update nixpkgs input to the latest nixos-unstable or nixpkgs-unstable.
                Run:
                  nix flake update nixpkgs
              '');
          in
          {
            imports = [
              (lib.modules.importApply ../machineModules/forName.nix {
                inherit (config.inventory) meta;
                inherit
                  name
                  directory
                  ;
              })
              # Import the correct 'core' module
              # We assume either:
              # - nixosModules (_class = nixos)
              # - darwinModules (_class = darwin)
              (lib.optionalAttrs (clan-core ? "${_class}Modules") clan-core."${_class}Modules".clanCore)
            ] ++ lib.optionals (_class == "nixos") (v.machineImports or [ ]);

            # default hostname
            networking.hostName = lib.mkDefault name;
          }
        )
      ) config.clanInternals.inventoryClass.machines)

      # The user can define some machine config here
      # i.e. 'clan.machines.jon = ...'
      config.machines
    ];

    specialArgs = {
      self = lib.mkDefault config.self;
    };

    # expose all machines as modules for re-use
    inherit nixosModules;
    inherit darwinModules;

    # Ready to use configurations
    # These are only shallow wrapping the 'nixosModules' or 'darwinModules' with
    # lib.nixosSystem
    inherit nixosConfigurations;
    inherit darwinConfigurations;

    clanInternals = {
      inventoryClass =
        let
          localModuleSet =
            lib.filterAttrs (n: _: !inventory._legacyModules ? ${n}) inventory.modules // config.modules;
          flakeInputs = config.self.inputs;
        in
        {
          _module.args = {
            inherit clanLib;
          };
          imports = [
            ../inventoryClass/builder/default.nix
            (lib.modules.importApply ../inventoryClass/service-list-from-inputs.nix {
              inherit localModuleSet flakeInputs clanLib;
            })
            {
              inherit inventory directory;
            }
            (
              { config, ... }:
              {
                distributedServices = clanLib.inventory.mapInstances {
                  inherit (config) inventory;
                  inherit localModuleSet flakeInputs;
                  prefix = [ "distributedServices" ];
                };
                machines = config.distributedServices.allMachines;
              }
            )
            ../inventoryClass/inventory-introspection.nix
          ];
        };

      # TODO: remove this after a month or so
      # This is here for backwards compatibility for older CLI versions
      inventory = config.inventory;

      # TODO: unify this interface
      # We should have only clan.modules. (consistent with clan.templates)
      inherit (clan-core) clanModules;

      # Statically export the predefined clan modules
      templates = clan-core.clan.templates;

      secrets = config.secrets;

      # machine specifics
      machines = configsPerSystem;
    };
  };
}
