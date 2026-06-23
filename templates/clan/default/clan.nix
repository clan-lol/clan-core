{
  # Ensure this is unique among all clans you want to use.
  meta.name = "{{name}}";
  meta.domain = "{{domain}}";

  inventory.machines = {
    # Define machines here.
    # test-machine = { };
  };

  inventory.instances = {

    # Docs: https://clan.lol/docs/services/official/sshd
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

    # Docs: https://clan.lol/docs/unstable/services/official/p2p-ssh-iroh
    # Status experimental
    # Firewall-traversing SSH access via encrypted QUIC streams
    # p2p-ssh-iroh = {
    #   roles.server.tags = [ "nixos" ];
    # };
  };

  # Additional NixOS configuration can be added here.
  # machines/server/configuration.nix will be automatically imported.
  # See: https://clan.lol/docs/unstable/guides/inventory/autoincludes
  machines = {
    # test-machine = { config, ... }: {
    #   environment.systemPackages = [ pkgs.asciinema ];
    # };
  };
}
