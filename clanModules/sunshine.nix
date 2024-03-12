{ pkgs, config, options, ... }:
let
  cfg = options.services.sunshine;
  sunshineConfiguration = pkgs.writeText "sunshine.conf" ''
    address_family = both
    channels = 5
    pkey = /var/lib/sunshine/sunshine.key
    cert = /var/lib/sunshine/sunshine.cert
    file_state = /var/lib/sunshine/state.json
    file_apps = /var/lib/sunshine/apps.json
    credentials_file = /var/lib/sunshine/credentials.json
  '';
in
{
  options.services.sunshine = {
    enable = pkgs.lib.mkEnableOption "Sunshine self-hosted game stream host for Moonlight";
  };

  config = pkgs.lib.mkMerge [
    (pkgs.lib.mkIf cfg.enable
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
                ${pkgs.sunshine}/bin/sunshine -1 ${
            pkgs.writeText "sunshine.conf" ''
                    address_family = both
                  ''
            } "$@"
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
        # services.udev.extraRules = ''
        #   KERNEL=="uinput", SUBSYSTEM=="misc", OPTIONS+="static_node=uinput", TAG+="uaccess"
        # '';
        services.udev.extraRules = ''
          KERNEL=="uinput", GROUP="input", MODE="0660" OPTIONS+="static_node=uinput"
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


        systemd.tmpfiles.rules = [
          "d '/var/lib/sunshine' 0770 'user' 'users' - -"
        ];


        systemd.user.services.sunshine = {
          enable = true;
          description = "Sunshine self-hosted game stream host for Moonlight";
          startLimitBurst = 5;
          startLimitIntervalSec = 500;
          script = "/run/current-system/sw/bin/env /run/wrappers/bin/sunshine ${sunshineConfiguration}";
          serviceConfig = {
            Restart = "on-failure";
            RestartSec = "5s";
            ReadWritePaths = [
              "/var/lib/sunshine"
            ];
          };
          wantedBy = [ "graphical-session.target" ];
        };
      }
    )
  ]
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
# }
