{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/ergochat";
  manifest.description = "A modern IRC server";
  manifest.categories = [ "Social" ];

  roles.default = {
    interface =
      { ... }:
      {
        options = { };
      };

    perInstance =
      { settings, ... }:
      {
        nixosModule =
          { ... }:
          {
            services.ergochat = {
              enable = true;

              settings = {
                datastore = {
                  autoupgrade = true;
                  path = "/var/lib/ergo/ircd.db";
                };
              };
            };

            clan.core.state.ergochat.folders = [ "/var/lib/ergo" ];
          };
      };
  };
}
