{ config, lib, ... }:
let
  instanceNames = builtins.attrNames config.clan.inventory.services.syncthing;
  instanceName = builtins.head instanceNames;
  instance = config.clan.inventory.services.syncthing.${instanceName};
  introducer = builtins.head instance.roles.introducer.machines;

  introducerId = "${config.clan.core.settings.directory}/vars/per-machine/${introducer}/syncthing/syncthing.pub/value";
in
{
  imports = [
    ../shared.nix
  ];
  clan.syncthing.introducer = lib.strings.removeSuffix "\n" (
    if builtins.pathExists introducerId
    then
      builtins.readFile introducerId
    else
      throw "${introducerId} does not exists. Please run `clan vars generate ${introducer}` to generate the introducer device id"
  );
}
