{ self, lib, ... }:
let
  clan-core = self;
in
{
  # Extension of the build clan interface
  # new_clan = clan-core.lib.buildClan {
  #   # High level services.
  #   # If you need multiple instances of a service configure them via:
  #   # inventory.services.[serviceName].[instanceName] = ...
  #   services = {
  #     borbackup = {
  #       roles.server.machines = [ "vyr" ];
  #       roles.client.tags = [ "laptop" ];
  #       machines.vyr = {
  #         config = {

  #         };
  #       };
  #       config = {

  #       };
  #     };
  #   };

  #   # Low level inventory i.e. if you need multiple instances of a service
  #   # Or if you want to manipulate the created inventory directly.
  #   inventory.services.borbackup.default = { };

  #   # Machines. each machine can be referenced by its attribute name under services.
  #   machines = {
  #     camina = {
  #       # This is added to machine tags
  #       clan.tags = [ "laptop" ];
  #       # These are the inventory machine fields
  #       clan.meta.description = "";
  #       clan.meta.name = "";
  #       clan.meta.icon = "";
  #       # Config ...
  #     };
  #     vyr = {
  #       # Config ...
  #     };
  #     vi = {
  #       clan.networking.targetHost = "root@78.47.164.46";
  #       # Config ...
  #     };
  #     aya = {
  #       clan.networking.targetHost = "root@78.47.164.46";
  #       # Config ...
  #     };
  #     ezra = {
  #       # Config ...
  #     };
  #     rianon = {
  #       # Config ...
  #     };
  #   };
  # };

  clan = clan-core.lib.buildClan {
    meta.name = "sams's clans";
    # Should usually point to the directory of flake.nix
    directory = self;

    # services = {
    #   borgbackup = {
    #     roles.server.machines = [ "vyr_machine" ];
    #     roles.client.tags = [ "laptop" ];
    #   };
    # };

    # OR
    inventory = builtins.fromJSON (builtins.readFile ./src/tests/borgbackup.json);

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
