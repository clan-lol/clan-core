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

  clanCore.state.thelounde.folders = [ "/var/lib/thelounge" ];
}
