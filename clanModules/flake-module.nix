{ ... }:
{
  flake.clanModules = {
    borgbackup = ./borgbackup;
    borgbackup-static = ./borgbackup-static;
    deltachat = ./deltachat;
    ergochat = ./ergochat;
    localbackup = ./localbackup;
    localsend = ./localsend;
    single-disk = ./single-disk;
    matrix-synapse = ./matrix-synapse;
    moonlight = ./moonlight;
    packages = ./packages;
    postgresql = ./postgresql;
    root-password = ./root-password;
    sshd = ./sshd;
    sunshine = ./sunshine;
    static-hosts = ./static-hosts;
    syncthing = ./syncthing;
    syncthing-static-peers = ./syncthing-static-peers;
    thelounge = ./thelounge;
    trusted-nix-caches = ./trusted-nix-caches;
    user-password = ./user-password;
    xfce = ./xfce;
    zerotier-static-peers = ./zerotier-static-peers;
    zt-tcp-relay = ./zt-tcp-relay;
  };
}
