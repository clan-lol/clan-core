{
  description = "<Put your description here>";

  inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  inputs.nixpkgs.follows = "clan-core/nixpkgs";
  inputs.flake-parts.url = "github:hercules-ci/flake-parts";
  inputs.flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";

  outputs =
    inputs@{
      self,
      clan-core,
      flake-parts,
      ...
    }:
    flake-parts.lib.mkFlake { inherit inputs; } ({
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      imports = [ inputs.clan-core.flakeModules.default ];
      # https://docs.clan.lol/getting-started/flake-parts/
      clan = {
        meta.name = "__CHANGE_ME__"; # Ensure this is unique among all clans you want to use.

        # Make flake available in modules
        specialArgs.self = {
          inherit (self) inputs nixosModules packages;
        };
        inherit self;
        machines = {
          # "jon" will be the hostname of the machine
          jon =
            { pkgs, ... }:
            {
              imports = [
                ./modules/shared.nix
                ./modules/disko.nix
                ./machines/jon/configuration.nix
              ];

              nixpkgs.hostPlatform = "x86_64-linux";

              # Set this for clan commands use ssh i.e. `clan machines update`
              # If you change the hostname, you need to update this line to root@<new-hostname>
              # This only works however if you have avahi running on your admin machine else use IP
              clan.core.networking.targetHost = pkgs.lib.mkDefault "root@jon";

              # You can get your disk id by running the following command on the installer:
              # Replace <IP> with the IP of the installer printed on the screen or by running the `ip addr` command.
              # ssh root@<IP> lsblk --output NAME,ID-LINK,FSTYPE,SIZE,MOUNTPOINT
              disko.devices.disk.main = {
                device = "/dev/disk/by-id/__CHANGE_ME__";
              };

              # IMPORTANT! Add your SSH key here
              # e.g. > cat ~/.ssh/id_ed25519.pub
              users.users.root.openssh.authorizedKeys.keys = throw ''
                Don't forget to add your SSH key here!
                users.users.root.openssh.authorizedKeys.keys = [ "<YOUR SSH_KEY>" ]
              '';

              # Zerotier needs one controller to accept new nodes. Once accepted
              # the controller can be offline and routing still works.
              clan.core.networking.zerotier.controller.enable = true;
            };
          # "sara" will be the hostname of the machine
          sara =
            { pkgs, ... }:
            {
              imports = [
                ./modules/shared.nix
                ./modules/disko.nix
                ./machines/sara/configuration.nix
              ];

              nixpkgs.hostPlatform = "x86_64-linux";

              # Set this for clan commands use ssh i.e. `clan machines update`
              # If you change the hostname, you need to update this line to root@<new-hostname>
              # This only works however if you have avahi running on your admin machine else use IP
              clan.core.networking.targetHost = pkgs.lib.mkDefault "root@sara";

              # You can get your disk id by running the following command on the installer:
              # Replace <IP> with the IP of the installer printed on the screen or by running the `ip addr` command.
              # ssh root@<IP> lsblk --output NAME,ID-LINK,FSTYPE,SIZE,MOUNTPOINT
              disko.devices.disk.main = {
                device = "/dev/disk/by-id/__CHANGE_ME__";
              };

              # IMPORTANT! Add your SSH key here
              # e.g. > cat ~/.ssh/id_ed25519.pub
              users.users.root.openssh.authorizedKeys.keys = throw ''
                Don't forget to add your SSH key here!
                users.users.root.openssh.authorizedKeys.keys = [ "<YOUR SSH_KEY>" ]
              '';

              /*
                After jon is deployed, uncomment the following line
                This will allow sara to share the VPN overlay network with jon
                The networkId is generated by the first deployment of jon
              */
              # clan.core.networking.zerotier.networkId = builtins.readFile ../jon/facts/zerotier-network-id;
            };
        };
      };
      perSystem =
        { pkgs, inputs', ... }:
        {
          devShells.default = pkgs.mkShell { packages = [ inputs'.clan-core.packages.clan-cli ]; };
        };
    });
}
