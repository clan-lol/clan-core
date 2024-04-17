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
    ergochat = ./ergochat.nix;
    deltachat = ./deltachat;
    graphical = ./graphical.nix;
    localbackup = ./localbackup.nix;
    localsend = ./localsend.nix;
    matrix-synapse = ./matrix-synapse.nix;
    moonlight = ./moonlight.nix;
    sshd = ./sshd.nix;
    sunshine = ./sunshine.nix;
    syncthing = ./syncthing;
    root-password = ./root-password;
    thelounge = ./thelounge.nix;
    vm-user = ./vm-user.nix;
    waypipe = ./waypipe.nix;
    xfce = ./xfce.nix;
    xfce-vm = ./xfce-vm.nix;
    zt-tcp-relay = ./zt-tcp-relay.nix;
  };
}
