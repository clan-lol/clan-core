{
  pkgs,
  ...
}:
let
  testPubKey = builtins.readFile ./test-key.pub;
in
{
  name = "sshd";

  clan = {
    directory = ./.;
    inventory = {
      machines.server = { };
      machines.client = { };

      instances = {
        sshd-test = {
          module.name = "@clan/sshd";
          module.input = "self";
          roles.server.machines."server".settings = {
            authorizedKeys.test-key = testPubKey;
            certificate.searchDomains = [ "example.com" ];
            hostKeys.rsa.enable = true;
          };
          roles.client.machines."client".settings = {
            certificate.searchDomains = [ "example.com" ];
          };
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

    # Check that sshd port is open on the server
    server.succeed("${pkgs.netcat}/bin/nc -z -v 127.0.0.1 22")

    # Check that /etc/ssh/ssh_known_hosts contains the required CA string on the server
    server.succeed("grep '^@cert-authority ssh-ca,\*.example.com ssh-ed25519 ' /etc/ssh/ssh_known_hosts")

    # Check that server contains a line starting with 'localhost,server ssh-ed25519'
    server.succeed("grep '^localhost,server,server.clan ssh-ed25519 ' /etc/ssh/ssh_known_hosts")

    # Check that /etc/ssh/ssh_known_hosts contains the required CA string on the client
    client.succeed("grep '^.cert-authority ssh-ca.*example.com ssh-ed25519 ' /etc/ssh/ssh_known_hosts")

    # Check that root's authorized_keys contains our manual test key
    server.succeed("grep 'test-key' /etc/ssh/authorized_keys.d/root")

    # Copy the test private key to the client and set permissions
    client.succeed("cp ${./test-key} /tmp/test-key && chmod 600 /tmp/test-key")

    # Test SSH authentication from client to server using the authorized key
    client.succeed("ssh -o StrictHostKeyChecking=accept-new -i /tmp/test-key root@server 'echo SSH_SUCCESS'")
  '';
}
