{ pkgs, config, ... }:
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
    pkgs.avahi
    # Convenience script, until we find a better UX
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
  boot.kernelModules = [ "uinput" ];
  security.rtkit.enable = true;

  # services.udev.extraRules = ''
  #   KERNEL=="uinput", SUBSYSTEM=="misc", OPTIONS+="static_node=uinput", TAG+="uaccess"
  # '';

  services.udev.extraRules = ''
    KERNEL=="uinput", GROUP="input", MODE="0660" OPTIONS+="static_node=uinput"
  '';

  security.wrappers.sunshine = {
    owner = "root";
    group = "root";
    capabilities = "cap_sys_admin+p";
    source = "${pkgs.sunshine}/bin/sunshine";
  };

  systemd.user.services.sunshine = {
    description = "sunshine";
    wantedBy = [ "graphical-session.target" ];
    environment = {
      DISPLAY = ":0";
    };
    serviceConfig = {
      ExecStart = "${config.security.wrapperDir}/sunshine";
    };
  };

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

  services = {
    avahi = {
      enable = true;
      reflector = true;
      nssmdns = true;
      publish = {
        enable = true;
        addresses = true;
        userServices = true;
        workstation = true;
      };
    };
  };
}
