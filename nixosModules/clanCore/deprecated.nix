{ lib, ... }:
let
  inherit (lib) mkRemovedOptionModule mkRenamedOptionModule;
in
{
  imports = [
    # == clan.inventory ==
    (mkRemovedOptionModule [ "clan" "inventory" "services" ] ''
      ###############################################################################
      #                                                                             #
      # Clan modules (clanModules) have been deprecated and removed in favor of     #
      # Clan services!                                                              #
      #                                                                             #
      # Refer to https://docs.clan.lol/guides/migrations/migrate-inventory-services #
      # for migration instructions.                                                 #
      #                                                                             #
      ###############################################################################
    '')
    (mkRemovedOptionModule [ "clan" "inventory" "assertions" ] ''
      Use of 'machine.<name>.config.clan.inventory.assertions' was replaced by 'clan.checks'
    '')

    # == clan.meta -> clan.core.settings ==
    (mkRenamedOptionModule [ "clan" "meta" "name" ] [ "clan" "core" "settings" "name" ])
    (mkRenamedOptionModule [ "clan" "meta" "description" ] [ "clan" "core" "settings" "description" ])
    (mkRenamedOptionModule [ "clan" "meta" "icon" ] [ "clan" "core" "settings" "icon" ])

    # == clan.core.clanName, etc. -> clan.core.settings ==
    (mkRemovedOptionModule [
      "clan"
      "core"
      "clanName"
    ] "clanName has been removed. Use clan.core.settings.name instead.")
    (mkRemovedOptionModule [
      "clan"
      "core"
      "clanIcon"
    ] "clanIcon has been removed. Use clan.core.settings.icon instead.")

    (mkRenamedOptionModule
      [ "clan" "core" "clanDir" ]
      [
        "clan"
        "core"
        "settings"
        "directory"
      ]
    )
    (mkRenamedOptionModule
      [ "clan" "core" "name" ]
      [
        "clan"
        "core"
        "settings"
        "name"
      ]
    )
    (mkRenamedOptionModule
      [ "clan" "core" "icon" ]
      [
        "clan"
        "core"
        "settings"
        "icon"
      ]
    )
    # The following options have been moved into clan.core.settings.machine
    (mkRenamedOptionModule
      [ "clan" "core" "machineName" ]
      [
        "clan"
        "core"
        "settings"
        "machine"
        "name"
      ]
    )
    (mkRenamedOptionModule
      [ "clan" "core" "machineDescription" ]
      [
        "clan"
        "core"
        "settings"
        "machine"
        "description"
      ]
    )
    (mkRenamedOptionModule
      [ "clan" "core" "machineIcon" ]
      [
        "clan"
        "core"
        "settings"
        "machine"
        "icon"
      ]
    )
  ];
}
