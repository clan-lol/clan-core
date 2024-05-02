{ inputs, ... }:
{
  flake.clanModules = {
    disk-layouts = {
      imports = [
        ./disk-layouts
        inputs.disko.nixosModules.default
      ];
    };
    borgbackup = ./borgbackup;
    ergochat = ./ergochat;
    deltachat = ./deltachat;
    graphical = ./graphical;
    localbackup = ./localbackup;
    localsend = ./localsend;
    matrix-synapse = ./matrix-synapse;
    moonlight = ./moonlight;
    sshd = ./sshd;
    sunshine = ./sunshine;
    syncthing = ./syncthing;
    root-password = ./root-password;
    thelounge = ./thelounge;
    vm-user = ./vm-user;
    xfce = ./xfce;
    xfce-vm = {
      imports = [
        ./vm-user
        ./graphical
        ./xfce-vm
      ];
    };
    zt-tcp-relay = ./zt-tcp-relay;
  };
}
