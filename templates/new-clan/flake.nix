{
  description = "<Put your description here>";

  inputs.clan-core.url = "git+https://git.clan.lol/clan/clan-core";

  outputs =
    { self, clan-core, ... }:
    let
      system = "x86_64-linux";
      pkgs = clan-core.inputs.nixpkgs.legacyPackages.${system};
      clan = clan-core.lib.buildClan {
        directory = self;
        clanName = "__CHANGE_ME__"; # Ensure this is internet wide unique.
        clanIcon = null; # Optional, a path to an image file
        # TODO: boot into the installer
        # remote> nixos-generate-config --root /tmp/config --no-filesystems
        # local> mkdir -p ./machines/machine1
        # local> scp -r root@machine1:/tmp/config ./machines/machine1
        # local> Edit ./machines/machine1/configuration.nix to your liking
        machines = {
          jon = {
            nixpkgs.hostPlatform = system;
            imports = [
              ./machines/jon/configuration.nix
              clan-core.clanModules.sshd
              clan-core.clanModules.diskLayouts
            ];
            config = {
              clanCore.machineIcon = null; # Optional, a path to an image file

              # Set this for clan commands use ssh i.e. `clan machines update`
              clan.networking.targetHost = pkgs.lib.mkDefault "root@<IP_ADDRESS>";

              # TODO: Example how to use disko for more complicated setups

              # remote> lsblk --output NAME,PTUUID,FSTYPE,SIZE,MOUNTPOINT
              clan.diskLayouts.singleDiskExt4 = {
                device = "/dev/disk/by-id/__CHANGE_ME__";
              };

              services.getty.autologinUser = "root";

              # TODO: Document that there needs to be one controller
              clan.networking.zerotier.controller.enable = true;
            };
          };
          sara = {
            nixpkgs.hostPlatform = system;
            imports = [
              ./machines/sara/configuration.nix
              clan-core.clanModules.sshd
              clan-core.clanModules.diskLayouts
            ];
            config = {
              clanCore.machineIcon = null; # Optional, a path to an image file

              # Set this for clan commands use ssh i.e. `clan machines update`
              clan.networking.targetHost = pkgs.lib.mkDefault "root@<IP_ADDRESS>";

              # local> clan facts generate

              clan.diskLayouts.singleDiskExt4 = {
                device = "/dev/disk/by-id/__CHANGE_ME__";
              };
            };
          };
        };
      };
    in
    {
      # all machines managed by cLAN
      inherit (clan) nixosConfigurations clanInternals;
      # add the cLAN cli tool to the dev shell
      devShells.${system}.default = pkgs.mkShell {
        packages = [ clan-core.packages.${system}.clan-cli ];
      };
    };
}
