{ ... }:

let
  error = builtins.throw ''
    clanModules have been removed!

    Refer to https://docs.clan.lol/guides/migrations/migrate-inventory-services for migration.
  '';

  modnames = [
    "auto-upgrade"
    "admin"
    "borgbackup"
    "borgbackup-static"
    "deltachat"
    "data-mesher"
    "disk-id"
    "dyndns"
    "ergochat"
    "garage"
    "heisenbridge"
    "importer"
    "iwd"
    "localbackup"
    "localsend"
    "matrix-synapse"
    "moonlight"
    "mumble"
    "mycelium"
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
    "wifi"
    "xfce"
    "zerotier"
    "zerotier-static-peers"
    "zt-tcp-relay"
  ];
in

{
  flake.clanModules = {
    outPath = "removed-clan-modules";
    value = error;
  };

  # builtins.listToAttrs (
  #   map (name: {
  #     inherit name;
  #     value = error;
  #   }) modnames
  # );
}
