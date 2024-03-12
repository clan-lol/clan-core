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
    sunshine = ./sunshine.nix;
    syncthing = ./syncthing.nix;
    vm-user = ./vm-user.nix;
    graphical = ./graphical.nix;
    xfce = ./xfce.nix;
    zt-tcp-relay = ./zt-tcp-relay.nix;
    localsend = ./localsend.nix;
    waypipe = ./waypipe.nix;
  };
}
