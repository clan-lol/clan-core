{ pkgs, ... }: {
  hardware.opengl.enable = true;
  environment.systemPackages = [ pkgs.moonlight-qt ];
}
