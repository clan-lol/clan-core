{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/kde";
  manifest.description = "Sets up a graphical desktop environment";
  manifest.categories = [ "Desktop" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.default = {
    description = "KDE/Plasma (wayland): Full-featured desktop environment with modern Qt-based interface";
    perInstance.nixosModule = {
      services = {
        displayManager.sddm.enable = true;
        displayManager.sddm.wayland.enable = true;
        desktopManager.plasma6.enable = true;
      };
    };
  };
}
