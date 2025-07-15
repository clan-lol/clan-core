{
  lib,
  config,
  pkgs,
  ...
}:
let
  dir = config.clan.core.settings.directory;
  machineDir = "${dir}/vars/per-machine";
  # TODO: This should use the inventory
  # However we are probably going to replace this with the network module.
  machinesFileSet = builtins.readDir machineDir;
  machines = lib.mapAttrsToList (name: _: name) machinesFileSet;

  networkIdsUnchecked = builtins.map (
    machine:
    let
      fullPath = "${machineDir}/vars/per-machine/${machine}/zerotier/zerotier-network-id/value";
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
      default = [ config.clan.core.settings.machine.name ];
      defaultText = lib.literalExpression "[ config.clan.core.settings.machine.name ]";
      description = "Hosts that should be excluded";
    };
    networkIps = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      description = "Extra zerotier network Ips that should be accepted";
    };
    networkIds = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      description = "Extra zerotier network Ids that should be accepted";
    };
  };

  config.systemd.services.zerotier-static-peers-autoaccept =
    let
      zerotierIpFor = machine: "${machineDir}/vars/per-machine/${machine}/zerotier/zerotier-ip/value";
      networkIpsUnchecked = builtins.map (
        machine: if builtins.pathExists (zerotierIpFor machine) then machine else null
      ) machines;
      networkIps = lib.filter (machine: machine != null) networkIpsUnchecked;
      machinesWithIp = lib.filterAttrs (name: _: (lib.elem name networkIps)) machinesFileSet;
      filteredMachines = lib.filterAttrs (
        name: _: !(lib.elem name config.clan.zerotier-static-peers.excludeHosts)
      ) machinesWithIp;
      hosts = lib.mapAttrsToList (host: _: host) (
        lib.mapAttrs' (
          machine: _: lib.nameValuePair (builtins.readFile (zerotierIpFor machine)) [ machine ]
        ) filteredMachines
      );
      allHostIPs = config.clan.zerotier-static-peers.networkIps ++ hosts;
    in
    lib.mkIf (config.clan.core.networking.zerotier.controller.enable) {
      wantedBy = [ "multi-user.target" ];
      after = [ "zerotierone.service" ];
      path = [ config.clan.core.clanPkgs.zerotierone ];
      serviceConfig.ExecStart = pkgs.writeScript "static-zerotier-peers-autoaccept" ''
        #!/bin/sh
        ${lib.concatMapStringsSep "\n" (host: ''
          ${config.clan.core.clanPkgs.zerotier-members}/bin/zerotier-members allow --member-ip ${host}
        '') allHostIPs}
        ${lib.concatMapStringsSep "\n" (host: ''
          ${config.clan.core.clanPkgs.zerotier-members}/bin/zerotier-members allow ${host}
        '') config.clan.zerotier-static-peers.networkIds}
      '';
    };

  config.clan.core.networking.zerotier.networkId = lib.mkDefault networkId;
}
