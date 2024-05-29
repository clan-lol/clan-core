{ lib, config, ... }:
{
  options.clan.static-hosts = {
    excludeHosts = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ config.clanCore.machineName ];
      description = "Hosts that should be excluded";
    };
    topLevelDomain = lib.mkOption {
      type = lib.types.str;
      default = "";
      description = "Top level domain to reach hosts";
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
    lib.filterAttrs (_: value: value != null) (
      lib.mapAttrs' (
        machine: _:
        let
          path = zerotierIpMachinePath machine;
        in
        if builtins.pathExists path then
          lib.nameValuePair (builtins.readFile path) (
            if (config.clan.static-hosts.topLevelDomain == "") then
              [ machine ]
            else
              [ "${machine}.${config.clan.static-hosts.topLevelDomain}" ]
          )
        else
          null
      ) filteredMachines
    );
}
