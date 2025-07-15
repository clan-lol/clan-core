{
  warnings = [
    "The clan.xfce module is deprecated and will be removed on 2025-07-15. Please migrate to user-maintained configuration."
  ];

  services.xserver = {
    enable = true;
    desktopManager.xfce.enable = true;
    layout = "us";
  };
}
