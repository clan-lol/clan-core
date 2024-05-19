{ ... }:
{
  flake.clanModules = {
    disk-layouts = {
      imports = [ ./disk-layouts ];
    };
    borgbackup = ./borgbackup;
    deltachat = ./deltachat;
    ergochat = ./ergochat;
    localbackup = ./localbackup;
    localsend = ./localsend;
    matrix-synapse = ./matrix-synapse;
    moonlight = ./moonlight;
    root-password = ./root-password;
    sshd = ./sshd;
    sunshine = ./sunshine;
    static-hosts = ./static-hosts;
    syncthing = ./syncthing;
    thelounge = ./thelounge;
    user-password = ./root-password;
    xfce = ./xfce;
    zt-tcp-relay = ./zt-tcp-relay;
  };
}
