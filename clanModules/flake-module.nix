{ ... }:

let
  error = builtins.throw ''

    ###############################################################################
    #                                                                             #
    # Clan modules (clanModules) have been deprecated and removed in favor of     #
    # Clan services!                                                              #
    #                                                                             #
    # Refer to https://docs.clan.lol/guides/migrations/migrate-inventory-services #
    # for migration instructions.                                                 #
    #                                                                             #
    ###############################################################################

  '';

  modnames = [
    "admin"
    "borgbackup"
    "borgbackup-static"
    "deltachat"
    "disk-id"
    "dyndns"
    "ergochat"
    "garage"
    "heisenbridge"
    "iwd"
    "localbackup"
    "localsend"
    "matrix-synapse"
    "moonlight"
    "mumble"
    "nginx"
    "packages"
    "postgresql"
    "root-password"
    "single-disk"
    "sshd"
    "state-version"
    "static-hosts"
    "sunshine"
    "syncthing"
    "syncthing-static-peers"
    "thelounge"
    "trusted-nix-caches"
    "user-password"
    "vaultwarden"
    "xfce"
    "zerotier-static-peers"
    "zt-tcp-relay"
  ];
in

{
  flake.clanModules = builtins.listToAttrs (
    map (name: {
      inherit name;
      value = error;
    }) modnames
  );
}
