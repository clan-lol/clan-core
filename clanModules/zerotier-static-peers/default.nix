{
  lib,
  config,
  pkgs,
  inputs,
  ...
}:
let
  clanDir = config.clanCore.clanDir;
  machineDir = clanDir + "/machines/";
  machinesFileSet = builtins.readDir machineDir;
  machines = lib.mapAttrsToList (name: _: name) machinesFileSet;

  zerotierNetworkIdPath = machines: machineDir + machines + "/facts/zerotier-network-id";
  networkIdsUnchecked = builtins.map (
    machine:
    let
      fullPath = zerotierNetworkIdPath machine;
    in
    if builtins.pathExists fullPath then builtins.readFile fullPath else null
  ) machines;
  networkIds = lib.filter (machine: machine != null) networkIdsUnchecked;
  networkId = if builtins.length networkIds == 0 then null else builtins.elemAt networkIds 0;
in
#TODO:trace on multiple found network-ids
#TODO:trace on no single found networkId
{
  options.clan.zerotier-static-peers = {
    excludeHosts = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ config.clanCore.machineName ];
      description = "Hosts that should be excluded";
    };
  };

  config.systemd.services.zerotier-static-peers-autoaccept =
    let
      machines = builtins.readDir machineDir;
      zerotierIpMachinePath = machines: machineDir + machines + "/facts/zerotier-ip";
      filteredMachines = lib.filterAttrs (
        name: _: !(lib.elem name config.clan.zerotier-static-peers.excludeHosts)
      ) machines;
      hosts = lib.mapAttrsToList (host: _: host) (
        lib.mapAttrs' (
          machine: _:
          let
            fullPath = zerotierIpMachinePath machine;
          in
          if builtins.pathExists fullPath then
            lib.nameValuePair (builtins.readFile fullPath) [ machine ]
          else
            null
        ) filteredMachines
      );
    in
    lib.mkIf (config.clan.networking.zerotier.controller.enable) {
      wantedBy = [ "multi-user.target" ];
      after = [ "zerotierone.service" ];
      path = [ pkgs.zerotierone ];
      serviceConfig.ExecStart = pkgs.writeScript "static-zerotier-peers-autoaccept" ''
        #!/bin/sh
        ${lib.concatMapStringsSep "\n" (host: ''
          ${
            inputs.clan-core.packages.${pkgs.system}.zerotier-members
          }/bin/zerotier-members allow --member-ip ${host}
        '') hosts}
      '';
    };

  config.clan.networking.zerotier.networkId = lib.mkDefault networkId;
}
