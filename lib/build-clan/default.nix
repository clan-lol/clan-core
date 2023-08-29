{ nixpkgs, clan, lib }:
{ directory  # The directory containing the machines subdirectory
, specialArgs ? { } # Extra arguments to pass to nixosSystem i.e. useful to make self available
, machines ? { } # allows to include machine-specific modules i.e. machines.${name} = { ... }
}:
let
  machinesDirs =
    if builtins.pathExists (directory + /machines)
    then builtins.readDir (directory + /machines)
    else { };

  machineSettings = machineName:
    if builtins.pathExists (directory + /machines/${machineName}/settings.json)
    then builtins.fromJSON (builtins.readFile (directory + /machines/${machineName}/settings.json))
    else { };

  nixosConfigurations = lib.mapAttrs
    (name: _mod:
      nixpkgs.lib.nixosSystem {
        modules = [
          (machineSettings name)
          (machines.${name} or { })
        ] ++ lib.attrValues clan.clanModules;
        specialArgs = specialArgs;
      })
    machinesDirs;
in
nixosConfigurations
