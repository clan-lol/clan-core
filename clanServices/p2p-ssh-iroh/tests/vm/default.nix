{
  pkgs,
  ...
}:
{
  name = "p2p-ssh-iroh";

  clan = {
    directory = ./.;
    inventory = {
      machines.server = { };
      machines.client = { };

      instances = {
        p2p-ssh-iroh-test = {
          module.name = "p2p-ssh-iroh";
          roles.server.machines."server" = { };
        };

        sshd = {
          module.name = "sshd";
          roles.server.machines."server" = { };
        };
      };
    };
  };

  nodes = {
    server = { };
    client = { };
  };

  testScript = ''
    start_all()

    # Verify sshd is listening
    server.wait_until_succeeds("${pkgs.netcat}/bin/nc -z -v 127.0.0.1 22")

    # Verify the dumbpipe listener service started
    server.wait_for_unit("p2p-ssh-iroh-p2p-ssh-iroh-test.service")

    # Verify the iroh secret credential was deployed
    server.succeed("test -f /run/credentials/p2p-ssh-iroh-p2p-ssh-iroh-test.service/iroh-secret")
  '';
}
