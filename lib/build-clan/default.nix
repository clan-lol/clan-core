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
    Distributed services configuration.

    This configures a default instance in the inventory with the name "default".

    If you need multiple instances of a service configure them via:
    inventory.services.[serviceName].[instanceName] = ...
  */
  services ? { },
  /*
    Low level inventory configuration.
    Overrides the services configuration.
  */
  inventory ? { },
}:
let
  _inventory =
    (
      if services != { } && inventory == { } then
        { services = lib.mapAttrs (_name: value: { default = value; }) services; }
      else if services == { } && inventory != { } then
        inventory
      else if services != { } && inventory != { } then
        throw "Either services or inventory should be set, but not both."
      else
        { }
    )
    // {
      machines = lib.mapAttrs (
        name: config:
        (lib.attrByPath [
          "clan"
          "meta"
        ] { } config)
        // {
          name = (
            lib.attrByPath [
              "clan"
              "meta"
              "name"
            ] name config
          );
          tags = lib.attrByPath [
            "clan"
            "tags"
          ] [ ] config;
        }
      ) machines;
    };

  buildInventory = import ./inventory.nix { inherit lib clan-core; };

  pkgs = import nixpkgs { };

  inventoryFile = builtins.toFile "inventory.json" (builtins.toJSON _inventory);

  # a Derivation that can be forced to validate the inventory
  # It is not used directly here.
  validatedFile = pkgs.stdenv.mkDerivation {
    name = "validated-inventory";
    src = ../../inventory/src;
    buildInputs = [ pkgs.cue ];
    installPhase = ''
      cue vet ${inventoryFile} root.cue -d "#Root"
      cp ${inventoryFile} $out
    '';
  };

  serviceConfigs = buildInventory _inventory;

  deprecationWarnings = [
    (lib.warnIf (
      clanName != null
    ) "clanName is deprecated, please use meta.name instead. ${clanName}" null)
    (lib.warnIf (clanIcon != null) "clanIcon is deprecated, please use meta.icon instead" null)
  ];

  machinesDirs = lib.optionalAttrs (builtins.pathExists "${directory}/machines") (
    builtins.readDir (directory + /machines)
  );

  mergedMeta =
    let
      metaFromFile =
        if (builtins.pathExists "${directory}/clan/meta.json") then
          let
            settings = builtins.fromJSON (builtins.readFile "${directory}/clan/meta.json");
          in
          settings
        else
          { };
      legacyMeta = lib.filterAttrs (_: v: v != null) {
        name = clanName;
        icon = clanIcon;
      };
      optionsMeta = lib.filterAttrs (_: v: v != null) meta;

      warnings =
        builtins.map (
          name:
          if
            metaFromFile.${name} or null != optionsMeta.${name} or null && optionsMeta.${name} or null != null
          then
            lib.warn "meta.${name} is set in different places. (exlicit option meta.${name} overrides ${directory}/clan/meta.json)" null
          else
            null
        ) (builtins.attrNames metaFromFile)
        ++ [ (if (res.name or null == null) then (throw "meta.name should be set") else null) ];
      res = metaFromFile // legacyMeta // optionsMeta;
    in
    # Print out warnings before returning the merged result
    builtins.deepSeq warnings res;

  machineSettings =
    machineName:
    # CLAN_MACHINE_SETTINGS_FILE allows to override the settings file temporarily
    # This is useful for doing a dry-run before writing changes into the settings.json
    # Using CLAN_MACHINE_SETTINGS_FILE requires passing --impure to nix eval
    if builtins.getEnv "CLAN_MACHINE_SETTINGS_FILE" != "" then
      builtins.fromJSON (builtins.readFile (builtins.getEnv "CLAN_MACHINE_SETTINGS_FILE"))
    else
      lib.optionalAttrs (builtins.pathExists "${directory}/machines/${machineName}/settings.json") (
        builtins.fromJSON (builtins.readFile (directory + /machines/${machineName}/settings.json))
      );

  # Read additional imports specified via a config option in settings.json
  # This is not an infinite recursion, because the imports are discovered here
  #   before calling evalModules.
  # It is still useful to have the imports as an option, as this allows for type
  #   checking and easy integration with the config frontend(s)
  machineImports =
    machineSettings: map (module: clan-core.clanModules.${module}) (machineSettings.clanImports or [ ]);

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
          settings
          clan-core.nixosModules.clanCore
          extraConfig
          (machines.${name} or { })
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

  allMachines = machinesDirs // machines;

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
    # Evaluated clan meta
    # Merged /clan/meta.json with overrides from buildClan
    meta = mergedMeta;
    inherit _inventory validatedFile;

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
