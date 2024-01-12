{ inputs, ... }: {
  flake.clanModules = {
    diskLayouts = {
      imports = [
        ./diskLayouts.nix
        inputs.disko.nixosModules.default
      ];
    };
    borgbackup = ./borgbackup.nix;
    deltachat = ./deltachat.nix;
    moonlight = ./moonlight.nix;
    syncthing = ./syncthing.nix;
    xfce = ./xfce.nix;
    zt-tcp-relay = ./zt-tcp-relay.nix;
  };
}
