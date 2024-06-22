{ self, lib, ... }:
let
  clan-core = self;
in
{
  clan = clan-core.lib.buildClan {

    meta.name = "kenjis clan";
    # Should usually point to the directory of flake.nix
    directory = self;

    # service config
    # Useful alias: "inventory.services.borgbackup.default"
    services = {
      borgbackup = {
        roles.server.machines = [ "vyr_machine" ];
        roles.client.tags = [ "laptop" ];
      };
    };

    # merged with
    inventory = builtins.fromJSON (builtins.readFile ./src/tests/borgbackup.json);

    # merged with
    machines = {
      "vyr_machine" = { };
      "vi_machine" = {
        clan.tags = [ "laptop" ];
      };
      "camina_machine" = {
        clan.tags = [ "laptop" ];
        clan.meta.name = "camina";
      };
    };
  };
}
