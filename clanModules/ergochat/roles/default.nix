_: {

  warnings = [
    "The clan.ergochat module is deprecated and will be removed on 2025-07-15. Please migrate to user-maintained configuration."
  ];

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
}
