# NixOS module
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
    machines
    pkgsForSystem
    specialArgs
    ;

  inherit (config.clanInternals) inventory;

  inherit (clan-core.lib.inventory) buildInventory;

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
    }
  );

  moduleSystemConstructor = {
    # TODO: remove default system once we have a hardware-config mechanism
    nixos =
      {
        system ? null,
        name,
        pkgs ? null,
        extraConfig ? { },
      }:
      nixpkgs.lib.nixosSystem {
        modules =
          let
            hwConfig = "${directory}/machines/${name}/hardware-configuration.nix";
            diskoConfig = "${directory}/machines/${name}/disko.nix";
          in
          [
            {
              # Autoinclude configuration.nix and hardware-configuration.nix
              imports = builtins.filter builtins.pathExists [
                "${directory}/machines/${name}/configuration.nix"
                hwConfig
                diskoConfig
              ];
            }
            clan-core.nixosModules.clanCore
            extraConfig
            (machines.${name} or { })
            # Inherit the inventory assertions ?
            # { inherit (mergedInventory) assertions; }
            { imports = inventoryClass.machines.${name}.machineImports or [ ]; }

            # Import the distribute services
            { imports = config.clanInternals.distributedServices.allMachines.${name} or [ ]; }
            (
              {
                # Settings
                clan.core.settings = {
                  inherit directory;
                  inherit (config.inventory.meta) name icon;

                  machine = {
                    inherit name;
                  };
                };
                # Inherited from clan wide settings
                # TODO: remove these

                networking.hostName = lib.mkDefault name;

                # For vars we need to override the system so we run vars
                # generators on the machine that runs `clan vars generate`. If a
                # users is using the `pkgsForSystem`, we don't set
                # nixpkgs.hostPlatform it would conflict with the `nixpkgs.pkgs`
                # option.
                nixpkgs.hostPlatform = lib.mkIf (system != null && (pkgsForSystem system) != null) (
                  lib.mkForce system
                );
              }
              // lib.optionalAttrs (pkgs != null) { nixpkgs.pkgs = lib.mkForce pkgs; }
            )
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
        extraConfig ? { },
      }:
      nix-darwin.lib.darwinSystem {
        modules = [
          {
            imports = builtins.filter builtins.pathExists [
              "${directory}/machines/${name}/configuration.nix"
            ];
          }
          (
            if !lib.hasAttrByPath [ "darwinModules" "clanCore" ] clan-core then
              { }
            else
              throw "this should import clan-core.darwinModules.clanCore"
          )
          extraConfig
          (machines.${name} or { })
          # TODO: import inventory when it has support for defining `nix-darwin` modules
          (
            {
              # TODO: set clan-core settings when clan-core has support for `nix-darwin`

              networking.hostName = lib.mkDefault name;

              # For vars we need to override the system so we run vars
              # generators on the machine that runs `clan vars generate`. If a
              # users is using the `pkgsForSystem`, we don't set
              # nixpkgs.hostPlatform it would conflict with the `nixpkgs.pkgs`
              # option.
              nixpkgs.hostPlatform = lib.mkIf (system != null && (pkgsForSystem system) != null) (
                lib.mkForce system
              );
            }
            // lib.optionalAttrs (pkgs != null) { nixpkgs.pkgs = lib.mkForce pkgs; }
          )
        ];

        specialArgs = {
          inherit clan-core;
        } // specialArgs;
      };
  };

  allMachines = inventoryClass.machines;

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

  configsFuncPerSystem = builtins.listToAttrs (
    builtins.map (
      system:
      lib.nameValuePair system (
        lib.mapAttrs (
          name: _: args:
          moduleSystemConstructor.${machineClasses.${name}} (
            args
            // {
              inherit name system;
              pkgs = pkgsFor.${system};
            }
          )
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
    moduleSchemas = clan-core.lib.modules.getModulesSchema config.inventory.modules;
    inherit inventoryClass;
    distributedServices = clan-core.clanLib.inventory.mapInstances {
      inherit inventory;
      flakeInputs = config.self.inputs;
    };
    # TODO: unify this interface
    # We should have only clan.modules. (consistent with clan.templates)
    inherit (clan-core) clanModules clanLib;
    modules = config.modules;

    inherit inventoryFile;
    inventoryValuesPrios =
      # Temporary workaround
      builtins.removeAttrs (clan-core.lib.values.getPrios { options = inventory.options; })
        # tags are freeformType which is not supported yet.
        [ "tags" ];

    templates = config.templates;
    inventory = config.inventory;
    meta = config.inventory.meta;

    source = "${clan-core}";

    # machine specifics
    machines = configsPerSystem;
    machinesFunc = configsFuncPerSystem;
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
