{ lib, config, ... }:
{
  options.clan.static-hosts = {
    excludeHosts = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ config.clanCore.machineName ];
      description = "Hosts that should be excluded";
    };
  };

  config.networking.hosts =
    let
      clanDir = config.clanCore.clanDir;
      machineDir = clanDir + "/machines/";
      zerotierIpMachinePath = machines: machineDir + machines + "/facts/zerotier-ip";
      machines = builtins.readDir machineDir;
      filteredMachines = lib.filterAttrs (
        name: _: !(lib.elem name config.clan.static-hosts.excludeHosts)
      ) machines;
    in
    (lib.mapAttrs' (
      machine: _: lib.nameValuePair (builtins.readFile (zerotierIpMachinePath machine)) [ machine ]
    ) filteredMachines);
}
