/*
  This is an example of a simple nixos module:

  Enables the GNOME desktop environment and the GDM display manager.

  To use this module, import it in your machines NixOS configuration like this:

  ```nix
  imports = [
    modules/gnome.nix
  ];
  ```
*/
{ ... }:
{
  services.xserver.enable = true;
  services.xserver.desktopManager.gnome.enable = true;
  services.xserver.displayManager.gdm.enable = true;
}
