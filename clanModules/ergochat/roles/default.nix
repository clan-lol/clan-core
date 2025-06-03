_: {
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
