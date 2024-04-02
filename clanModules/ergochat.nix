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

  clanCore.state.ergochat.folders = [ "/var/lib/ergo" ];
}
