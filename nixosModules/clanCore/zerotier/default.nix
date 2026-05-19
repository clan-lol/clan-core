{
  lib,
  ...
}:
let
  zerotierMigrationMessage = ''
    Direct ZeroTier option configuration has been removed.
    ZeroTier is now configured through the clan inventory system.

    To set up ZeroTier networking, define it as a service in your inventory
    and assign the "controller" and "peer" roles to your machines.

    See the inventory guide: https://clan.lol/docs/unstable/guides/inventory/intro-to-inventory
    See the networking guide: https://clan.lol/docs/unstable/guides/networking/networking
  '';
in
{
  imports =

    [
      # Previous "enable" switch
      # If people have enabled zerotier via our old nixos-option
      # Print migration message, zerotier should be used via inventory like any other service.
      (lib.mkRemovedOptionModule [
        "clan"
        "core"
        "networking"
        "zerotier"
        "networkId"
      ] zerotierMigrationMessage)

      # Previous turn this machine into a "controller" switch
      # People should use the "controller" role
      (lib.mkRemovedOptionModule [
        "clan"
        "core"
        "networking"
        "zerotier"
        "controller"
        "enable"
      ] zerotierMigrationMessage)
    ];
}
