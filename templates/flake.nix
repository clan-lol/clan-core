{
  outputs =
    { ... }:
    let
      templates = {
        disko = {
          btrfs-single-disk-subvolumes = {
            description = "Single disk schema with Btrfs subvolumes and automated btrbk snapshots";
            path = ./disk/btrfs-single-disk-subvolumes;
          };
          btrfs-single-disk-subvolumes-impermanance-script = {
            description = "Single disk schema with Btrfs subvolumes, Btrfs-based ephemeral root (rollback), and automated btrbk snapshots";
            path = ./disk/btrfs-single-disk-subvolumes-impermanance-script;
          };
          btrfs-single-disk-subvolumes-impermanance-tmpfs = {
            description = "Single disk schema with Btrfs subvolumes, ephemeral tmpfs root, and automated btrbk snapshots";
            path = ./disk/btrfs-single-disk-subvolumes-impermanance-tmpfs;
          };
          ext4-single-disk = {
            description = "A simple ext4 disk with a single partition";
            path = ./disk/ext4-single-disk;
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
          flake-parts-minimal = {
            description = "Minimal flake-parts clan template";
            path = ./clan/flake-parts-minimal;
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
