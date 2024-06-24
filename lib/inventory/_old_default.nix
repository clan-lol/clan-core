{ self, lib, ... }:
let
  clan-core = self;
in
{
  clan = clan-core.lib.buildClan {
    meta.name = "kenjis clan";
    # Should usually point to the directory of flake.nix
    directory = self;

    inventory = {
      services = {
        borgbackup.instance_1 = {
          roles.server.machines = [ "vyr_machine" ];
          roles.client.tags = [ "laptop" ];
        };
      };
    };

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
