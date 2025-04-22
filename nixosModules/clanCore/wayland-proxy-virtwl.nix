{
  pkgs,
  config,
  lib,
  ...
}:
{
  _class = "nixos";
  options = {
    # maybe upstream this?
    services.wayland-proxy-virtwl = {
      enable = lib.mkEnableOption "wayland-proxy-virtwl";
      package = lib.mkPackageOption pkgs "wayland-proxy-virtwl" { };
    };
  };
  config = lib.mkIf config.services.wayland-proxy-virtwl.enable {
    programs.xwayland.enable = lib.mkDefault true;
    environment.etc."X11/xkb".source = config.services.xserver.xkb.dir;

    environment.sessionVariables = {
      WAYLAND_DISPLAY = "wayland-1";
      DISPLAY = ":1";
      QT_QPA_PLATFORM = "wayland"; # Qt Applications
      GDK_BACKEND = "wayland"; # GTK Applications
      XDG_SESSION_TYPE = "wayland"; # Electron Applications
      SDL_VIDEODRIVER = "wayland";
      CLUTTER_BACKEND = "wayland";
    };

    # Is there a better way to do this?
    programs.bash.loginShellInit = ''
      if [ "$(tty)" = "/dev/ttyS0" ]; then
        systemctl --user start graphical-session.target
      fi
    '';

    systemd.user.services.wayland-proxy-virtwl = {
      description = "Wayland proxy for virtwl";
      before = [ "graphical-session.target" ];
      wantedBy = [ "graphical-session.target" ];
      serviceConfig = {
        Type = "simple";
        ExecStart = "${config.services.wayland-proxy-virtwl.package}/bin/wayland-proxy-virtwl --virtio-gpu --x-display=1 --xwayland-binary=${pkgs.xwayland}/bin/Xwayland";
        Restart = "always";
        RestartSec = 5;
      };
    };
  };
}
