{ config }: {
  imports = [
    config.clanCore.clanModules.vm-user
    config.clanCore.clanModules.graphical
  ];

  services.xserver = {
    enable = true;
    displayManager.autoLogin.enable = true;
    displayManager.autoLogin.user = "user";
    desktopManager.xfce.enable = true;
    desktopManager.xfce.enableScreensaver = false;
    xkb.layout = "us";
  };
}
