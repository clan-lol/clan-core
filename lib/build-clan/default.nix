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

  nixosConfiguration = { system ? "x86_64-linux", name }: nixpkgs.lib.nixosSystem {
    modules = [
      self.nixosModules.clanCore
      (machineSettings name)
      (machines.${name} or { })
      {
        clanCore.machineName = name;
        clanCore.clanDir = directory;
        # TODO: remove this once we have a hardware-config mechanism
        nixpkgs.hostPlatform = lib.mkDefault system;
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
  # clanInternals.machinesForAllSystems.<system>.<machine>
  # We need this to build nixos secret generators for each system
  machinesForAllSystems = builtins.listToAttrs
    (builtins.map
      (system: lib.nameValuePair system
        (lib.mapAttrs (name: _: nixosConfiguration { inherit name system; }) allMachines))
      supportedSystems);
in
{
  inherit nixosConfigurations;

  clanInternals = {
    machines = lib.mapAttrs
      (_: lib.mapAttrs (_: machine: {
        inherit (machine.config.system.clan) uploadSecrets generateSecrets;
        inherit (machine.config.clan.networking) deploymentAddress;
      }))
      machinesForAllSystems;
  };
}
