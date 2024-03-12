{
  imports = [
    ./vm-user.nix
    ./graphical.nix
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
