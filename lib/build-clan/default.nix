{ nixpkgs, self, lib }:
{ directory  # The directory containing the machines subdirectory
, specialArgs ? { } # Extra arguments to pass to nixosSystem i.e. useful to make self available
, machines ? { } # allows to include machine-specific modules i.e. machines.${name} = { ... }
}:
let
  machinesDirs = lib.optionalAttrs (builtins.pathExists "${directory}/machines") (builtins.readDir (directory + /machines));

  machineSettings = machineName:
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

  getMachine = machine: {
    inherit (machine.config.system.clan) uploadSecrets generateSecrets;
    inherit (machine.config.clan.networking) deploymentAddress;
  };

  machinesPerSystem = lib.mapAttrs (_: machine: getMachine machine);

  machinesPerSystemWithJson = lib.mapAttrs (_: machine:
    let
      m = getMachine machine;
    in
    m // {
      json = machine.pkgs.writers.writeJSON "machine.json" m;
    });
in
{
  inherit nixosConfigurations;

  clanInternals = {
    machines = lib.mapAttrs (_: configs: machinesPerSystemWithJson configs) configsPerSystem;
    machines-json = lib.mapAttrs (system: configs: nixpkgs.legacyPackages.${system}.writers.writeJSON "machines.json" (machinesPerSystem configs)) configsPerSystem;
  };
}
