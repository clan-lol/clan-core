{
  clan-core,
  nixpkgs,
  lib,
}:
{
  directory, # The directory containing the machines subdirectory
  specialArgs ? { }, # Extra arguments to pass to nixosSystem i.e. useful to make self available
  machines ? { }, # allows to include machine-specific modules i.e. machines.${name} = { ... }
  clanName, # Needs to be (globally) unique, as this determines the folder name where the flake gets downloaded to.
  clanIcon ? null, # A path to an icon to be used for the clan, should be the same for all machines
  pkgsForSystem ? (_system: null), # A map from arch to pkgs, if specified this nixpkgs will be only imported once for each system.
# This improves performance, but all nipxkgs.* options will be ignored.
}:
let
  machinesDirs = lib.optionalAttrs (builtins.pathExists "${directory}/machines") (
    builtins.readDir (directory + /machines)
  );

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
          (
            {
              networking.hostName = lib.mkDefault name;
              clanCore.clanName = clanName;
              clanCore.clanIcon = clanIcon;
              clanCore.clanDir = directory;
              clanCore.machineName = name;
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
{
  inherit nixosConfigurations;

  clanInternals = {
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
