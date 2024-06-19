{ lib, config, ... }:
let
  clanDir = config.clan.core.clanDir;
  machineDir = clanDir + "/machines/";

  cfg = config.clan.borgbackup-static;

  machine_name = config.clan.core.machineName;
in
{
  imports = [ ../borgbackup ];

  # Inventory / Interface.nix
  # options.clan.inventory.borgbackup-static.description.
  options.clan.borgbackup-static.roles = lib.mkOption {
    type = lib.types.attrsOf (lib.types.listOf lib.types.str);
  };

  config.services.borgbackup.repos =
    let

      filteredMachines = builtins.attrNames (lib.filterAttrs (_: v: builtins.elem "client" v) cfg.roles);

      borgbackupIpMachinePath = machines: machineDir + machines + "/facts/borgbackup.ssh.pub";
      machinesMaybeKey = builtins.map (
        machine:
        let
          fullPath = borgbackupIpMachinePath machine;
        in
        if builtins.pathExists fullPath then machine else null
      ) filteredMachines;

      machinesWithKey = lib.filter (x: x != null) machinesMaybeKey;

      hosts = builtins.map (machine: {
        name = machine;
        value = {
          path = "/var/lib/borgbackup/${machine}";
          authorizedKeys = [ (builtins.readFile (borgbackupIpMachinePath machine)) ];
        };
      }) machinesWithKey;
    in
    lib.mkIf (builtins.elem "server" cfg.roles.${machine_name}) (
      if (builtins.listToAttrs hosts) != null then builtins.listToAttrs hosts else { }
    );

  config.clan.borgbackup.destinations =
    let
      servers = builtins.attrNames (lib.filterAttrs (_n: v: (builtins.elem "server" v)) cfg.roles);

      destinations = builtins.map (server_name: {
        name = server_name;
        value = {
          repo = "borg@${server_name}:/var/lib/borgbackup/${machine_name}";
        };
      }) servers;
    in
    lib.mkIf (builtins.elem "client" cfg.roles.${machine_name}) (builtins.listToAttrs destinations);
}
