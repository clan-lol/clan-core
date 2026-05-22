{
  lib,
  ...
}:
let
  zerotierMigrationMessage = ''
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
      (lib.mkRemovedOptionModule
        [
          "clan"
          "core"
          "networking"
          "zerotier"
          "networkId"
        ]
        ''
          Direct ZeroTier option configuration has been removed.
          ZeroTier is now configured through the clan inventory system.

          ${zerotierMigrationMessage}
        ''
      )

      # Previous turn this machine into a "controller" switch
      # People should use the "controller" role
      (lib.mkRemovedOptionModule
        [
          "clan"
          "core"
          "networking"
          "zerotier"
          "controller"
          "enable"
        ]
        ''
          Direct ZeroTier option configuration has been removed.
          ZeroTier is now configured through the clan inventory system.

          ${zerotierMigrationMessage}
        ''
      )

      (lib.mkRemovedOptionModule
        [
          "clan"
          "core"
          "networking"
          "zerotier"
          "controller"
          "public"
        ]
        ''
          To make a zerotier network public use the inventory settings for the controller role.

          ${zerotierMigrationMessage}
        ''
      )

      (lib.mkRemovedOptionModule
        [
          "clan"
          "core"
          "networking"
          "zerotier"
          "moon"
          "stableEndpoints"
        ]
        ''
          Moon stable endpoints are now configured through the moon role settings in the inventory.

          ${zerotierMigrationMessage}
        ''
      )

      (lib.mkRemovedOptionModule
        [
          "clan"
          "core"
          "networking"
          "zerotier"
          "moon"
          "orbitMoons"
        ]
        ''
          External moon orbiting is now configured through the peer role settings in the inventory.

          ${zerotierMigrationMessage}
        ''
      )

      (lib.mkRemovedOptionModule
        [
          "clan"
          "core"
          "networking"
          "zerotier"
          "settings"
        ]
        ''
          Direct network settings override has been removed.
          Controller network configuration is now managed by the clanService.

          ${zerotierMigrationMessage}
        ''
      )
    ];
}
