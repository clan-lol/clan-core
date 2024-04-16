{ ... }:
{
  imports = [ ./hardware-configuration.nix ];
  users.users.root.openssh.authorizedKeys.keys = [
    # IMPORTANT! Add your SSH key here
    # e.g. > cat ~/.ssh/id_ed25519.pub
    "<YOUR SSH_KEY>"
  ];

  services.xserver.enable = true;
  services.xserver.desktopManager.gnome.enable = true;
  services.xserver.displayManager.gdm.enable = true;
  # Disable the default gnome apps to speed up deployment
  services.gnome.core-utilities.enable = false;
}
