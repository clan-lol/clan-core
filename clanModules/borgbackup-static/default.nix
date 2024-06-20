{ lib, config, ... }:
let
  clanDir = config.clan.core.clanDir;
  machineDir = clanDir + "/machines/";

  # cfg.roles = config.clan.borgbackup-static;

  # machine < machine_module  < inventory
  #  nixos  < borgbackup      < borgbackup-static > UI
  #                           metadata
  #              Developer    User field descriptions

  roles = config.clan.borgbackup-static.inventory.roles;

  machine_name = config.clan.core.machineName;
in
{
  imports = [ ../borgbackup ];
  # imports = if myRole == "server" then [ ../borgbackup/roles/server.nix ];
  # Inventory / Interface.nix
  # options.clan.inventory.borgbackup-static.description.
  # options.clan.borgbackup-static.roles = lib.mkOption {
  #   type = lib.types.attrsOf (lib.types.listOf lib.types.str);
  # };

  # Can be used via inventory.json
  #
  # .borgbackup-static.inventory.roles
  #
  options.clan.borgbackup-static.inventory = lib.mkOption {
    type = lib.types.submodule {
      # imports = [./inventory/interface.nix];

      # idea
      # config.metadata = builtins.fromTOML ...
      # config.defaultRoles = ["client"];

      # -> interface.nix
      options = {
        roles = lib.mkOption { type = lib.types.attrsOf (lib.types.listOf lib.types.str); };
      };
    };
  };

  config.services.borgbackup.repos =
    let

      filteredMachines = builtins.attrNames (lib.filterAttrs (_: v: builtins.elem "client" v) roles);

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
    lib.mkIf (builtins.elem "server" roles.${machine_name}) (
      if (builtins.listToAttrs hosts) != null then builtins.listToAttrs hosts else { }
    );

  config.clan.borgbackup.destinations =
    let
      servers = builtins.attrNames (lib.filterAttrs (_n: v: (builtins.elem "server" v)) roles);

      destinations = builtins.map (server_name: {
        name = server_name;
        value = {
          repo = "borg@${server_name}:/var/lib/borgbackup/${machine_name}";
        };
      }) servers;
    in
    lib.mkIf (builtins.elem "client" roles.${machine_name}) (builtins.listToAttrs destinations);
}
