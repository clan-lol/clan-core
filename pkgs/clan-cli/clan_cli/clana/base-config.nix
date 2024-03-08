{ config, ... }:

{
  imports =
    [
      # Include the results of the hardware scan.
      ./hardware-configuration.nix
    ];

  # Ensure that software properties (e.g., being unfree) are respected.
  nixpkgs.config = {
    allowUnfree = true;
  };

  # Use the systemd-boot EFI boot loader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "clana"; # Define your hostname.
  networking.networkmanager.enable = true;

  # Enable the X11 windowing system.
  services.xserver.enable = true;
  services.xserver.layout = "us";
  services.xserver.xkbOptions = "eurosign:e";

  # Enable touchpad support.
  services.xserver.libinput.enable = true;

  # Enable the KDE Desktop Environment.
  services.xserver.displayManager.sddm.enable = true;
  services.xserver.desktopManager.plasma5.enable = true;

  # Enable sound.
  sound.enable = true;
  hardware.pulseaudio.enable = true;

  # Autologin settings.
  services.xserver.displayManager.autoLogin.enable = true;
  services.xserver.displayManager.autoLogin.user = "user";

  # User settings.
  users.users.user = {
    isNormalUser = true;
    extraGroups = [ "wheel" ]; # Enable sudo for the user.
    uid = 1000;
    password = "hello";
    openssh.authorizedKeys.keys = [ ];
  };

  # Enable firewall.
  networking.firewall.enable = true;
  networking.firewall.allowedTCPPorts = [ 80 443 ]; # HTTP and HTTPS

  # Set time zone.
  time.timeZone = "UTC";

  # System-wide settings.
  system.stateVersion = "22.05"; # Edit this to your NixOS release version.
}
