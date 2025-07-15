_: {
  warnings = [
    "The clan.thelounge module is deprecated and will be removed on 2025-07-15. Please migrate to user-maintained configuration."
  ];

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
