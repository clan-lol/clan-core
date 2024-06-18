_: {
  services.thelounge = {
    enable = true;
    public = true;
    extraConfig = {
      prefetch = true;
      defaults = {
        port = 6667;
        tls = false;
      };
    };
  };

  clan.core.state.thelounde.folders = [ "/var/lib/thelounge" ];
}
