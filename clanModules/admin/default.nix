{ config, ... }:
{
  config.assertions = [
    {
      assertion = config.clan.inventory.services.admin != { };
      message = ''
        The admin module has been migrated from `clan.services` to `clan.instances`
        See https://docs.clan.lol/TODO for updated usage.
      '';
    }
  ];
}
