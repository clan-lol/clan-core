{
  lib,
  pkgs,
  ...
}:
{
  imports = [
    ../installer.nix
    ../nouveau-workaround.nix
    ../vga-primary-console.nix
  ];

  # Use kmscon as the terminal emulator
  # This provides proper font rendering and VT handling
  services.kmscon = {
    enable = true;
    hwRender = false; # Software rendering is more compatible

    fonts = [
      {
        name = "DejaVu Sans Mono";
        package = pkgs.dejavu_fonts;
      }
    ];

    extraConfig = ''
      font-size=16
    '';
  };

  # Autologin is handled by agetty; kmscon follows getty's setting
  services.getty.autologinUser = lib.mkForce "root";

  # Less ipv6 addresses to reduce the noise
  networking.tempAddresses = "disabled";

  # Tango theme for serial console fallback
  # kmscon uses its own palette
  console.colors = lib.mkDefault [
    "000000"
    "CC0000"
    "4E9A06"
    "C4A000"
    "3465A4"
    "75507B"
    "06989A"
    "D3D7CF"
    "555753"
    "EF2929"
    "8AE234"
    "FCE94F"
    "739FCF"
    "AD7FA8"
    "34E2E2"
    "EEEEEC"
  ];
}
