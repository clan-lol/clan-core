The `sshd` Clan service manages SSH to make it easy to securely access your
machines over the internet. The service uses `vars` to store the SSH host keys
for each machine to ensure they remain stable across deployments.

`sshd` also generates SSH certificates for both servers and clients allowing for
certificate-based authentication for SSH.

The service also disables password-based authentication over SSH, to access your
machines you'll need to use public key authentication or certificate-based
authentication.

## Usage
```nix
{
  inventory.instances = {
    # By default this service only generates ed25519 host keys
    sshd-basic = {
      module = {
        name = "sshd";
        input = "clan-core";
      };
      roles.server.tags.all = { };
      roles.client.tags.all = { };
    };
    # Also generate RSA host keys for all servers
    sshd-with-rsa = {
      module = {
        name = "sshd";
        input = "clan-core";
      };
      roles.server.tags.all = { };
      roles.server.settings = {
        hostKeys.rsa.enable = true;
      };
      roles.client.tags.all = { };
    };
  };
}
```
