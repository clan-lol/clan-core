{
  # Ensure this is unique among all clans you want to use.
  meta.name = "{{name}}";
  meta.domain = "{{domain}}";

  inventory.machines = {
    # Define machines here.
    # server = { };
  };

  # Docs: See https://docs.clan.lol/latest/services/definition/
  inventory.instances = {

    # Docs: https://docs.clan.lol/latest/services/official/sshd/
    # SSH service for secure remote access to machines.
    # Generates persistent host keys and configures authorized keys.
    sshd = {
      roles.server.tags.all = { };
      roles.server.settings.authorizedKeys = {
        # Insert the public key that you want to use for SSH access.
        # All keys will have ssh access to all machines ("tags.all" means 'all machines').
        # Alternatively set 'users.users.root.openssh.authorizedKeys.keys' in each machine
        "admin-machine-1" = "__YOUR_PUBLIC_KEY__";
      };
    };

    # Docs: https://docs.clan.lol/latest/services/official/users/
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

    # Docs: https://docs.clan.lol/latest/services/official/zerotier/
    # The lines below will define a zerotier network and add all machines as 'peer' to it.
    # !!! Manual steps required:
    #   - Define a controller machine for the zerotier network.
    #   - Deploy the controller machine first to initialize the network.
    zerotier = {
      # Replace with the name (string) of your machine that you will use as zerotier-controller
      # See: https://docs.zerotier.com/controller/
      # Deploy this machine first to create the network secrets
      roles.controller.machines."__YOUR_CONTROLLER__" = { };
      # Peers of the network
      # tags.all means 'all machines' will joined
      roles.peer.tags.all = { };
    };

    # Docs: https://docs.clan.lol/latest/services/official/tor/
    # Tor network provides secure, anonymous connections to your machines
    # All machines will be accessible via Tor as a fallback connection method
    tor = {
      roles.server.tags.nixos = { };
    };
  };

  # Additional NixOS configuration can be added here.
  # machines/server/configuration.nix will be automatically imported.
  # See: https://docs.clan.lol/latest/guides/inventory/autoincludes/
  machines = {
    # server = { config, ... }: {
    #   environment.systemPackages = [ pkgs.asciinema ];
    # };
  };
}
