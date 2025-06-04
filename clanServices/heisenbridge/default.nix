{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/heisenbridge";
  manifest.description = "A matrix bridge to communicate with IRC";
  manifest.categories = [ "Social" ];

  roles.default = {
    interface =
      { lib, ... }:
      {
        options.homeserver = lib.mkOption {
          type = lib.types.str;
          default = "http://localhost:8008";
          description = "URL of the Matrix homeserver";
        };
      };

    perInstance =
      { settings, ... }:
      {
        nixosModule = {

          services.heisenbridge = {
            enable = true;
            homeserver = settings.homeserver;
          };

          services.matrix-synapse.settings.app_service_config_files = [
            "/var/lib/heisenbridge/registration.yml"
          ];
        };
      };
  };
}
