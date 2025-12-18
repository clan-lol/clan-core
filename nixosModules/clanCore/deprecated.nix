{ lib, ... }:
let
  inherit (lib) mkRemovedOptionModule mkRenamedOptionModule;
in
{
  imports = [
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

    (mkRenamedOptionModule [ "clan" "meta" "name" ] [ "clan" "core" "settings" "name" ])
    (mkRenamedOptionModule [ "clan" "meta" "description" ] [ "clan" "core" "settings" "description" ])
    (mkRenamedOptionModule [ "clan" "meta" "icon" ] [ "clan" "core" "settings" "icon" ])
  ];
}
