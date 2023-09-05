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

  nixosConfigurations = lib.mapAttrs
    (name: _:
      nixpkgs.lib.nixosSystem {
        modules = [
          self.nixosModules.clanCore
          (machineSettings name)
          (machines.${name} or { })
          {
            clanCore.machineName = name;
            clanCore.clanDir = directory;
            # TODO: remove this once we have a hardware-config mechanism
            nixpkgs.hostPlatform = lib.mkDefault "x86_64-linux";
          }
        ];
        inherit specialArgs;
      })
    (machinesDirs // machines);
in
nixosConfigurations
