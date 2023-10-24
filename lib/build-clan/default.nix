{ nixpkgs, self, lib }:
{ directory  # The directory containing the machines subdirectory
, specialArgs ? { } # Extra arguments to pass to nixosSystem i.e. useful to make self available
, machines ? { } # allows to include machine-specific modules i.e. machines.${name} = { ... }
}:
let
  machinesDirs = lib.optionalAttrs (builtins.pathExists "${directory}/machines") (builtins.readDir (directory + /machines));

  machineSettings = machineName:
    if builtins.getEnv "CLAN_MACHINE_SETTINGS_FILE" != ""
    then builtins.fromJSON (builtins.readFile (builtins.getEnv "CLAN_MACHINE_SETTINGS_FILE"))
    else
      lib.optionalAttrs (builtins.pathExists "${directory}/machines/${machineName}/settings.json")
        (builtins.fromJSON
          (builtins.readFile (directory + /machines/${machineName}/settings.json)));

  # TODO: remove default system once we have a hardware-config mechanism
  nixosConfiguration = { system ? "x86_64-linux", name }: nixpkgs.lib.nixosSystem {
    modules = [
      self.nixosModules.clanCore
      (machineSettings name)
      (machines.${name} or { })
      {
        clanCore.machineName = name;
        clanCore.clanDir = directory;
        nixpkgs.hostPlatform = lib.mkForce system;
      }
    ];
    inherit specialArgs;
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
  configsPerSystem = builtins.listToAttrs
    (builtins.map
      (system: lib.nameValuePair system
        (lib.mapAttrs (name: _: nixosConfiguration { inherit name system; }) allMachines))
      supportedSystems);
in
{
  inherit nixosConfigurations;

  clanInternals = {
    machines = configsPerSystem;
    all-machines-json = lib.mapAttrs
      (system: configs: nixpkgs.legacyPackages.${system}.writers.writeJSON "machines.json" (lib.mapAttrs (_: m: m.config.system.clan.deployment.data) configs))
      configsPerSystem;
  };
}
