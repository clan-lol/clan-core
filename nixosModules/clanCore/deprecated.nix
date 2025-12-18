{ lib, ... }:
{
  imports = [
    (lib.mkRemovedOptionModule [ "clan" "inventory" "services" ] ''
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
    (lib.mkRemovedOptionModule [ "clan" "inventory" "assertions" ] ''
      Use of 'machine.<name>.config.clan.inventory.assertions' was replaced by 'clan.checks'
    '')
  ];
}
