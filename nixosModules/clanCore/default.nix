{
  imports = [
    ./backups.nix
    ./facts
    ./manual.nix
    ./imports.nix
    ./metadata.nix
    ./networking.nix
    ./nix-settings.nix
    ./options.nix
    ./outputs.nix
    ./packages.nix
    ./schema.nix
    ./vm.nix
    ./wayland-proxy-virtwl.nix
    ./zerotier
    # Inventory
    ./inventory/interface.nix
    ./meta/interface.nix
    ./vars
  ];
}
