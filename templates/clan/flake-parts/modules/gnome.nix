{ ... }:
{
  # Can be imported into machines to enable GNOME and GDM.
  #
  # Copy this into a machine's configuration:
  # `machines/<name>/configuration.nix`
  # ```nix
  # imports = [
  #   ../../modules/gnome.nix
  # ];
  # ```

  # Enable the GNOME desktop environment and the GDM display manager.
  # Pre NixOS: 25.11
  # services.xserver.enable = true;
  # services.xserver.displayManager.gdm.enable = true;
  # services.xserver.desktopManager.gnome.enable = true;

  # => 25.11
  # services.displayManager.gdm.enable = true;
  # services.desktopManager.gnome.enable = true;

}
