{
  clan-core,
  nixpkgs,
  lib,
}:
{
  directory, # The directory containing the machines subdirectory
  specialArgs ? { }, # Extra arguments to pass to nixosSystem i.e. useful to make self available
  machines ? { }, # allows to include machine-specific modules i.e. machines.${name} = { ... }
  # DEPRECATED: use meta.name instead
  clanName ? null, # Needs to be (globally) unique, as this determines the folder name where the flake gets downloaded to.
  # DEPRECATED: use meta.icon instead
  clanIcon ? null, # A path to an icon to be used for the clan, should be the same for all machines
  meta ? { }, # A set containing clan meta: name :: string, icon :: string, description :: string
  # A map from arch to pkgs, if specified this nixpkgs will be only imported once for each system.
  # This improves performance, but all nipxkgs.* options will be ignored.
  pkgsForSystem ? (_system: null),
  /*
    Low level inventory configuration.
    Overrides the services configuration.
  */
  inventory ? { },
}:
let
  # Internal inventory, this is the result of merging all potential inventory sources:
  # - Default instances configured via 'services'
  # - The inventory overrides
  #   - Machines that exist in inventory.machines
  # - Machines explicitly configured via 'machines' argument
  # - Machines that exist in the machines directory
  # Checks on the module level:
  # - Each service role must reference a valid machine after all machines are merged

  clanToInventory =
    config:
    { clanPath, inventoryPath }:
    let
      v = lib.attrByPath clanPath null config;
    in
    lib.optionalAttrs (v != null) (lib.setAttrByPath inventoryPath v);

  mergedInventory =
    (lib.evalModules {
      modules = [
        clan-core.lib.inventory.interface
        { inherit meta; }
        (
          if
            builtins.pathExists "${directory}/inventory.json"
          # Is recursively applied. Any explicit nix will override.
          then
            (builtins.fromJSON (builtins.readFile "${directory}/inventory.json"))
          else
            { }
        )
        inventory
        # Machines explicitly configured via 'machines' argument
        {
          # { ${name} :: meta // { name, tags } }
          machines = lib.mapAttrs (
            name: machineConfig:
            (lib.attrByPath [
              "clan"
              "meta"
            ] { } machineConfig)
            // {
              # meta.name default is the attribute name of the machine
              name = lib.mkDefault (
                lib.attrByPath [
                  "clan"
                  "meta"
                  "name"
                ] name machineConfig
              );
            }
            # tags
            // (clanToInventory machineConfig {
              clanPath = [
                "clan"
                "tags"
              ];
              inventoryPath = [ "tags" ];
            })
            # system
            // (clanToInventory machineConfig {
              clanPath = [
                "nixpkgs"
                "hostPlatform"
              ];
              inventoryPath = [ "system" ];
            })
            # deploy.targetHost
            // (clanToInventory machineConfig {
              clanPath = [
                "clan"
                "core"
                "networking"
                "targetHost"
              ];
              inventoryPath = [
                "deploy"
                "targetHost"
              ];
            })
          ) machines;
        }

        # Will be deprecated
        {
          machines =
            lib.mapAttrs
              (
                name: _:
                # Use mkForce to make sure users migrate to the inventory system.
                # When the settings.json exists the evaluation will print the deprecation warning.
                lib.mkForce {
                  inherit name;
                  system = (machineSettings name).nixpkgs.hostSystem or null;
                }
              )
              (
                lib.filterAttrs (
                  machineName: _: builtins.pathExists "${directory}/machines/${machineName}/settings.json"
                ) machinesDirs
              );
        }

        # Deprecated interface
        (if clanName != null then { meta.name = clanName; } else { })
        (if clanIcon != null then { meta.icon = clanIcon; } else { })
      ];
    }).config;

  inherit (clan-core.lib.inventory) buildInventory;

  # map from machine name to service configuration
  # { ${machineName} :: Config }
  serviceConfigs = buildInventory {
    inventory = mergedInventory;
    inherit directory;
  };

  machinesDirs = lib.optionalAttrs (builtins.pathExists "${directory}/machines") (
    builtins.readDir (directory + /machines)
  );

  machineSettings =
    machineName:
    let
      warn = lib.warn ''
        The use of ./machines/<machine>/settings.json is deprecated.
        If your settings.json is empty, you can safely remove it.
        !!! Consider using the inventory system. !!!

        File: ${directory + /machines/${machineName}/settings.json}

        If there are still features missing in the inventory system, please open an issue on the clan-core repository.
      '';
    in
    # CLAN_MACHINE_SETTINGS_FILE allows to override the settings file temporarily
    # This is useful for doing a dry-run before writing changes into the settings.json
    # Using CLAN_MACHINE_SETTINGS_FILE requires passing --impure to nix eval
    if builtins.getEnv "CLAN_MACHINE_SETTINGS_FILE" != "" then
      warn (builtins.fromJSON (builtins.readFile (builtins.getEnv "CLAN_MACHINE_SETTINGS_FILE")))
    else
      lib.optionalAttrs (builtins.pathExists "${directory}/machines/${machineName}/settings.json") (
        warn (builtins.fromJSON (builtins.readFile (directory + /machines/${machineName}/settings.json)))
      );

  machineImports =
    machineSettings: map (module: clan-core.clanModules.${module}) (machineSettings.clanImports or [ ]);

  deprecationWarnings = [
    (lib.warnIf (
      clanName != null
    ) "clanName in buildClan is deprecated, please use meta.name instead." null)
    (lib.warnIf (clanIcon != null) "clanIcon is deprecated, please use meta.icon instead" null)
  ];

  # TODO: remove default system once we have a hardware-config mechanism
  nixosConfiguration =
    {
      system ? "x86_64-linux",
      name,
      pkgs ? null,
      extraConfig ? { },
    }:
    nixpkgs.lib.nixosSystem {
      modules =
        let
          settings = machineSettings name;
        in
        (machineImports settings)
        ++ [
          {
            # Autoinclude configuration.nix and hardware-configuration.nix
            imports = builtins.filter (p: builtins.pathExists p) [
              "${directory}/machines/${name}/configuration.nix"
              "${directory}/machines/${name}/hardware-configuration.nix"
            ];
          }
          settings
          clan-core.nixosModules.clanCore
          extraConfig
          (machines.${name} or { })
          # Inherit the inventory assertions ?
          { inherit (mergedInventory) assertions; }
          { imports = serviceConfigs.${name} or { }; }
          (
            {
              # Settings
              clan.core.clanDir = directory;
              # Inherited from clan wide settings
              clan.core.clanName = meta.name or clanName;
              clan.core.clanIcon = meta.icon or clanIcon;

              # Machine specific settings
              clan.core.machineName = name;
              networking.hostName = lib.mkDefault name;
              nixpkgs.hostPlatform = lib.mkDefault system;

              # speeds up nix commands by using the nixpkgs from the host system (especially useful in VMs)
              nix.registry.nixpkgs.to = {
                type = "path";
                path = lib.mkDefault nixpkgs;
              };
            }
            // lib.optionalAttrs (pkgs != null) { nixpkgs.pkgs = lib.mkForce pkgs; }
          )
        ];
      specialArgs = {
        inherit clan-core;
      } // specialArgs;
    };

  allMachines = mergedInventory.machines or { };

  supportedSystems = [
    "x86_64-linux"
    "aarch64-linux"
    "riscv64-linux"
    "x86_64-darwin"
    "aarch64-darwin"
  ];

  nixosConfigurations = lib.mapAttrs (name: _: nixosConfiguration { inherit name; }) allMachines;

  # This instantiates nixos for each system that we support:
  # configPerSystem = <system>.<machine>.nixosConfiguration
  # We need this to build nixos secret generators for each system
  configsPerSystem = builtins.listToAttrs (
    builtins.map (
      system:
      lib.nameValuePair system (
        lib.mapAttrs (
          name: _:
          nixosConfiguration {
            inherit name system;
            pkgs = pkgsForSystem system;
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
          nixosConfiguration (
            args
            // {
              inherit name system;
              pkgs = pkgsForSystem system;
            }
          )
        ) allMachines
      )
    ) supportedSystems
  );
in
builtins.deepSeq deprecationWarnings {
  inherit nixosConfigurations;

  clanInternals = {
    inherit (clan-core) clanModules;
    source = "${clan-core}";

    meta = mergedInventory.meta;
    inventory = mergedInventory;

    inventoryFile = "${directory}/inventory.json";

    # machine specifics
    machines = configsPerSystem;
    machinesFunc = configsFuncPerSystem;
    all-machines-json = lib.mapAttrs (
      system: configs:
      nixpkgs.legacyPackages.${system}.writers.writeJSON "machines.json" (
        lib.mapAttrs (_: m: m.config.system.clan.deployment.data) configs
      )
    ) configsPerSystem;
  };
}
