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
    localbackup = ./localbackup;
    localsend = ./localsend;
    matrix-synapse = ./matrix-synapse;
    moonlight = ./moonlight;
    sshd = ./sshd;
    sunshine = ./sunshine;
    syncthing = ./syncthing;
    root-password = ./root-password;
    thelounge = ./thelounge;
    xfce = ./xfce;
    zt-tcp-relay = ./zt-tcp-relay;
  };
}
