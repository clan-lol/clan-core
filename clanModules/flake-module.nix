{ inputs, ... }: {
  flake.clanModules = {
    diskLayouts = {
      imports = [
        ./diskLayouts.nix
        inputs.disko.nixosModules.default
      ];
    };
    deltachat = ./deltachat.nix;
    xfce = ./xfce.nix;
    borgbackup = ./borgbackup.nix;
    syncthing = ./syncthing.nix;
    zt-tcp-relay = ./zt-tcp-relay.nix;
  };
}
