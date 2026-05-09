{
  # Ensure this is unique among all clans you want to use.
  meta.name = "{{name}}";
  meta.domain = "{{domain}}";

  inventory.machines = {
    # Define machines here.
    # server = { };
    installer-machine = {
      tags = [ "installer-tag" ];
    };
  };

  # Docs: See https://clan.lol/docs/unstable/services/definition
  inventory.instances = {

    # Docs: https://clan.lol/docs/unstable/services/official/installer
    # Adds required packages for remote installation to all machines with the 'installer-tag'
    installer-module = {
      module = {
        name = "installer";
      };
      roles.iso.tags = [ "installer-tag" ];
    };

    # Docs: https://clan.lol/docs/unstable/services/official/p2p-ssh-iroh
    # Firewall-traversing SSH access via encrypted QUIC streams
    p2p-ssh-iroh = {
      roles.server.tags = [ "nixos" ];
    };

    # Docs: https://clan.lol/docs/unstable/services/official/sshd
    # SSH service for secure remote access to machines.
    # Generates persistent host keys and configures authorized keys.
    sshd = {
      roles.server.tags.all = { };
      roles.server.settings.authorizedKeys = {
        # Insert the public key that you want to use for SSH access.
        # All keys will have ssh access to all machines ("tags.all" means 'all machines').
        # Alternatively set 'users.users.root.openssh.authorizedKeys.keys' in each machine
        "admin-machine-1" = "PASTE_YOUR_KEY_HERE";
      };
    };

    # Docs: https://clan.lol/docs/unstable/services/official/users
    # Root password management for all machines.
    user-root = {
      module = {
        name = "users";
      };
      roles.default.tags.all = { };
      roles.default.settings = {
        user = "root";
        prompt = true;
      };
    };

  };

  # Additional NixOS configuration can be added here.
  # machines/server/configuration.nix will be automatically imported.
  # See: https://clan.lol/docs/unstable/guides/inventory/autoincludes
  machines = {
    # server = { config, ... }: {
    #   environment.systemPackages = [ pkgs.asciinema ];
    # };
  };
}
