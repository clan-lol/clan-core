{
  lib,
  ...
}:
{
  imports = [
    (lib.mkRemovedOptionModule [
      "clan"
      "heisenbridge"
      "enable"
    ] "Importing the module will already enable the service.")
  ];
  config = {
    warnings = [
      "The clan.heisenbridge module is deprecated and will be removed on 2025-07-15.
      Please migrate to user-maintained configuration or the new equivalent clan services
      (https://docs.clan.lol/reference/clanServices)."
    ];
    services.heisenbridge = {
      enable = true;
      homeserver = "http://localhost:8008"; # TODO: Sync with matrix-synapse
    };
    services.matrix-synapse.settings.app_service_config_files = [
      "/var/lib/heisenbridge/registration.yml"
    ];
  };
}
