{ lib, ... }:
{
  imports = [
    (lib.mkRemovedOptionModule [
      "clan"
      "postgresql"
    ] "The postgresql module has been migrated to a clan core option. Use clan.core.postgresql instead")
  ];
}
