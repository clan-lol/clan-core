{
  security = {
    sudo.wheelNeedsPassword = false;
    polkit.enable = true;
    rtkit.enable = true;
  };

  users.users.user = {
    isNormalUser = true;
    createHome = true;
    uid = 1000;
    initialHashedPassword = "";
    extraGroups = [
      "wheel"
      "video"
      "render"
    ];
    shell = "/run/current-system/sw/bin/bash";
  };
}
