{ config, lib, ... }:
let
  instances = config.clan.services.borgbackup;
  # roles = { ${role_name} :: { machines :: [string] } }
  allServers = lib.foldlAttrs (
    acc: _instanceName: instanceConfig:
    acc
    ++ (
      if builtins.elem machineName instanceConfig.roles.client.machines then
        instanceConfig.roles.server.machines
      else
        [ ]
    )
  ) [ ] instances;

  inherit (config.clan.core) machineName;
in
{
  config.clan.borgbackup.destinations =
    let

      destinations = builtins.map (serverName: {
        name = serverName;
        value = {
          repo = "borg@${serverName}:/var/lib/borgbackup/${machineName}";
        };
      }) allServers;
    in
    (builtins.listToAttrs destinations);
}
