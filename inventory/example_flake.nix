{
  description = "<Put your description here>";

  inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";

  outputs =
    { clan-core, ... }:
    let
      pkgs = clan-core.inputs.nixpkgs.legacyPackages.${system};
      # Usage see: https://docs.clan.lol

      #  nice_flake_interface -> buildClan() -> inventory -> buildClanFromInventory() -> nixosConfigurations

      system = "x86_64-linux";

      clan =
        clan-core.lib.buildClanFromInventory [
          # Inventory 0 (loads the json file managed by the Python API)
          (builtins.fromJSON (builtins.readFile ./inventory.json))
          # ->
          # {
          #   services."backups_1".autoIncludeMachines = true;
          #   services."backups_1".module = "borgbackup";
          #   ... etc.
          # }
        ]
        ++ buildInventory {
          clanName = "nice_flake_interface";
          description = "A nice flake interface";
          icon = "assets/icon.png";
          machines = {
            jon = {
              # Just regular nixos/clan configuration ?
              # config = {
              #   imports = [
              #     ./modules/shared.nix
              #     ./machines/jon/configuration.nix
              #   ];
              #   nixpkgs.hostPlatform = system;
              #   # Set this for clan commands use ssh i.e. `clan machines update`
              #   # If you change the hostname, you need to update this line to root@<new-hostname>
              #   # This only works however if you have avahi running on your admin machine else use IP
              #   clan.networking.targetHost = pkgs.lib.mkDefault "root@jon";
              #   # ssh root@flash-installer.local lsblk --output NAME,ID-LINK,FSTYPE,SIZE,MOUNTPOINT
              #   disko.devices.disk.main = {
              #     device = "/dev/disk/by-id/__CHANGE_ME__";
              #   };
              #   # IMPORTANT! Add your SSH key here
              #   # e.g. > cat ~/.ssh/id_ed25519.pub
              #   users.users.root.openssh.authorizedKeys.keys = throw ''
              #     Don't forget to add your SSH key here!
              #     users.users.root.openssh.authorizedKeys.keys = [ "<YOUR SSH_KEY>" ]
              #   '';
              #   # Zerotier needs one controller to accept new nodes. Once accepted
              #   # the controller can be offline and routing still works.
              #   clan.networking.zerotier.controller.enable = true;
              # };
            };
          };
        }
        ++ [
          # Low level inventory overrides (comes at the end)
          {
            services."backups_2".autoIncludeMachines = true;
            services."backups_2".module = "borgbackup";
          }
        ];

      /*
        # Type

        buildInventory :: {
          clanName :: string
          machines :: {
            ${name} :: {
              config :: {
                # NixOS configuration
              };
            };
          };
          # ... More mapped inventory options
          # i.e. shared config for all machines
        } -> Inventory
      */
      buildInventory =
        options:
        let
          # TODO: Map over machines
          name = "jon";
          inventory = {
            # Set the clan meta
            meta.name = options.clanName;
            meta.description = options.description;
            meta.icon = options.icon;
            # Declare the services
            # This "nixos" module simply provides the usual NixOS configuration options.
            services."nixos".module = "nixos";
            services."nixos".machineConfig.${name}.config = options.machines.${name}.config;

            # Declare the machines
            machines.${name} = {
              name = options.machines.${name}.meta.name;
              description = options.machines.${name}.meta.description;
              icon = options.machines.${name}.meta.icon;
              system = options.machines.${name}.config.nixpkgs.hostPlatform;
            };
          };
        in
        inventory;
    in
    {
      # all machines managed by Clan
      inherit (clan) nixosConfigurations clanInternals;
      # add the Clan cli tool to the dev shell
      devShells.${system}.default = pkgs.mkShell {
        packages = [ clan-core.packages.${system}.clan-cli ];
      };
    };
}
