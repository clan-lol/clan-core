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
        machines = {
          jon = {
            nixpkgs.hostPlatform = system;
            imports = [
              # TODO: boot into the installer
              # remote> nixos-generate-config --root /tmp/config --no-filesystems
              # local> mkdir -p ./machines/machine1
              # local> scp -r root@machine1:/tmp/config ./machines/machine1
              # local> Edit ./machines/machine1/configuration.nix to your liking
              ./modules/disko.nix
              ./machines/jon/configuration.nix
              clan-core.clanModules.sshd
              {
                # Set this for clan commands use ssh i.e. `clan machines update`
                clan.networking.targetHost = pkgs.lib.mkDefault "root@<IP_ADDRESS>";
                # remote> lsblk --output NAME,PTUUID,FSTYPE,SIZE,MOUNTPOINT

                config.disko.devices.disk.main.device = "/dev/disk/by-id/__CHANGE_ME__";

                clan.networking.zerotier.controller.enable = true;
              }
            ];
          };
          sara = {
            nixpkgs.hostPlatform = system;
            imports = [
              # ./machines/machine2/configuration.nix
              ./modules/disko.nix
              ./machines/sara/configuration.nix
              clan-core.clanModules.sshd
              {
                # Set this for clan commands use ssh i.e. `clan machines update`
                clan.networking.targetHost = pkgs.lib.mkDefault "root@<IP_ADDRESS>";

                config.disko.devices.disk.main.device = "/dev/disk/by-id/__CHANGE_ME__";
                # local> clan facts generate
                clan.networking.zerotier.networkId = builtins.readFile ./machines/machine1/facts/zerotier-network-id;
              }
            ];
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
