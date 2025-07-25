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

  services.displayManager.gdm.enable = true;
  services.desktopManager.gnome.enable = true;
}
