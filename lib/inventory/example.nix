{ self, ... }:
self.lib.buildClan {
  # Name of the clan in the UI, should be unique
  meta.name = "Inventory clan";

  # Should usually point to the directory of flake.nix
  directory = self;

  inventory = {
    services = {
      borgbackup.instance_1 = {
        roles.server.machines = [ "backup_server" ];
        roles.client.tags = [ "backup" ];
      };
    };
  };

  # merged with
  machines = {
    "backup_server" = {
      clan.tags = [ "all" ];
    };
    "client_1_machine" = {
      clan.tags = [
        "all"
        "backup"
      ];
    };
    "client_2_machine" = {
      clan.tags = [
        "all"
        "backup"
      ];
      # Name of the machine in the UI
      clan.meta.name = "camina";
    };
  };
}
