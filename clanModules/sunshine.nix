{ pkgs, options, ... }:
let
  apps = pkgs.writeText "apps.json" (
    builtins.toJSON {
      env = {
        PATH = "$(PATH):$(HOME)/.local/bin:/run/current-system/sw/bin";
      };
      apps = [
        {
          name = "Desktop";
          image-path = "desktop.png";
        }
        {
          name = "Low Res Desktop";
          image-path = "desktop.png";
          prep-cmd = [
            {
              do = "xrandr --output HDMI-1 --mode 1920x1080";
              undo = "xrandr --output HDMI-1 --mode 1920x1200";
            }
          ];
        }
        {
          name = "Steam Big Picture";
          detached = [ "setsid steam steam://open/bigpicture" ];
          image-path = "steam.png";
        }
      ];
    }
  );
  sunshineConfiguration = pkgs.writeText "sunshine.conf" ''
    address_family = both
    channels = 5
    pkey = /var/lib/sunshine/sunshine.key
    cert = /var/lib/sunshine/sunshine.cert
    file_state = /var/lib/sunshine/state.json
    file_apps = ${apps}
    credentials_file = /var/lib/sunshine/credentials.json
  '';
in
{
  options.services.sunshine = {
    enable = pkgs.lib.mkEnableOption "Sunshine self-hosted game stream host for Moonlight";
  };

  imports = [
    {
      networking.firewall = {
        allowedTCPPorts = [
          47984
          47989
          47990
          48010
        ];

        allowedUDPPorts = [
          47998
          47999
          48000
          48002
          48010
        ];
      };
      networking.firewall.allowedTCPPortRanges = [
        {
          from = 47984;
          to = 48010;
        }
      ];
      networking.firewall.allowedUDPPortRanges = [
        {
          from = 47998;
          to = 48010;
        }
      ];

      environment.systemPackages = [
        pkgs.sunshine
        (pkgs.writers.writeDashBin "sun" ''
          ${pkgs.sunshine}/bin/sunshine -1 ${pkgs.writeText "sunshine.conf" ''
            address_family = both
          ''} "$@"
        '')
        # Create a dummy account, for easier setup,
        # don't use this account in actual production yet.
        (pkgs.writers.writeDashBin "init-sun" ''
          ${pkgs.sunshine}/bin/sunshine \
          --creds "sun" "sun"
        '')
      ];

      # Required to simulate input
      hardware.uinput.enable = true;
      boot.kernelModules = [ "uinput" ];

      services.udev.extraRules = ''
        KERNEL=="uinput", SUBSYSTEM=="misc", OPTIONS+="static_node=uinput", TAG+="uaccess"
      '';

      hardware.opengl.driSupport32Bit = true;
      hardware.opengl.enable = true;

      security = {
        rtkit.enable = true;
        wrappers.sunshine = {
          owner = "root";
          group = "root";
          capabilities = "cap_sys_admin+p";
          source = "${pkgs.sunshine}/bin/sunshine";
        };
      };

      systemd.tmpfiles.rules = [ "d '/var/lib/sunshine' 0770 'user' 'users' - -" ];

      systemd.user.services.sunshine = {
        enable = true;
        description = "Sunshine self-hosted game stream host for Moonlight";
        startLimitBurst = 5;
        startLimitIntervalSec = 500;
        script = "/run/current-system/sw/bin/env /run/wrappers/bin/sunshine ${sunshineConfiguration}";
        serviceConfig = {
          Restart = "on-failure";
          RestartSec = "5s";
          ReadWritePaths = [ "/var/lib/sunshine" ];
        };
        wantedBy = [ "graphical-session.target" ];
      };
    }
  ];
  # xdg.configFile."sunshine/apps.json".text = builtins.toJSON {
  #   env = "/run/current-system/sw/bin";
  #   apps = [
  #     {
  #       name = "Steam";
  #       output = "steam.txt";
  #       detached = [
  #         "${pkgs.util-linux}/bin/setsid ${pkgs.steam}/bin/steam steam://open/bigpicture"
  #       ];
  #       image-path = "steam.png";
  #     }
  #   ];
  # };
}
