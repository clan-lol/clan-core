{
  outputs =
    { ... }:
    let
      templates = {
        disko = {
          single-disk = {
            description = "A simple ext4 disk with a single partition";
            path = ./disk/single-disk;
          };
        };

        machine = {
          flash-installer = {
            description = "Initialize a new flash-installer machine";
            path = ./machine/flash-installer;
          };

          new-machine = {
            description = "Initialize a new machine";
            path = ./machine/new-machine;
          };
        };

        clan = {
          default = {
            description = "Initialize a new clan flake";
            path = ./clan/default;
          };
          minimal = {
            description = "for clans managed via (G)UI";
            path = ./clan/minimal;
          };
          flake-parts = {
            description = "Flake-parts";
            path = ./clan/flake-parts;
          };
        };
      };
    in
    rec {
      inherit (clan) clanInternals;

      clan.clanInternals.templates = templates;
      clan.templates = templates;
    };
}
