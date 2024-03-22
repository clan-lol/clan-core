{ inputs, ... }:
{
  flake.clanModules = {
    diskLayouts = {
      imports = [
        ./diskLayouts.nix
        inputs.disko.nixosModules.default
      ];
    };
    borgbackup = ./borgbackup.nix;
    localbackup = ./localbackup.nix;
    deltachat = ./deltachat.nix;
    matrix-synapse = ./matrix-synapse.nix;
    moonlight = ./moonlight.nix;
    sunshine = ./sunshine.nix;
    syncthing = ./syncthing.nix;
    sshd = ./sshd.nix;
    vm-user = ./vm-user.nix;
    graphical = ./graphical.nix;
    xfce = ./xfce.nix;
    xfce-vm = ./xfce-vm.nix;
    zt-tcp-relay = ./zt-tcp-relay.nix;
    localsend = ./localsend.nix;
    waypipe = ./waypipe.nix;
  };
}
