!!! Danger "Experimental"
    This service is experimental and will change in the future.

---

This service will set up data-mesher, a file synchronization daemon that uses 
a gossip protocol to replicate files across a cluster of nodes.

## Architecture

Data-mesher v2 uses a file-based approach where:

- Files are defined with a list of authorized public keys (ED25519)
- Only files listed in the configuration can be uploaded or synced
- Files must be signed by one of the configured public keys

## Roles

- **admin**: A node that can sign files and act as a bootstrap node
- **peer**: A node that participates in the cluster and can receive files

## Usage

```nix
inventory.instances = {
  data-mesher = {
    module = {
      name = "data-mesher";
      input = "clan-core";
    };
    roles.admin.machines.server0.settings = {
      network.interface = "tailscale0";
      bootstrapNodes = [
        "192.168.1.1:7946"
        "192.168.1.2:7946"
      ];
      # Define which files can be synced and their authorized signers
      files = {
        "config:app" = [
          "azwT+VhTxA+BF73Hwq0uqdXHG8XvHU2BknoVXgmEjww="  # admin key
        ];
        "shared:data" = [
          "azwT+VhTxA+BF73Hwq0uqdXHG8XvHU2BknoVXgmEjww="  # admin key
          "Mdtz9s2DEyEk0DL8ZzW7WqwAehoQ97PFHVbJJdskkGo="  # peer key
        ];
      };
    };
    roles.peer.machines.server1.settings = {
      network.interface = "tailscale0";
      bootstrapNodes = [
        "192.168.1.1:7946"
        "192.168.1.2:7946"
      ];
      # Peers need the same file definitions to participate in syncing
      files = {
        "config:app" = [
          "azwT+VhTxA+BF73Hwq0uqdXHG8XvHU2BknoVXgmEjww="
        ];
        "shared:data" = [
          "azwT+VhTxA+BF73Hwq0uqdXHG8XvHU2BknoVXgmEjww="
          "Mdtz9s2DEyEk0DL8ZzW7WqwAehoQ97PFHVbJJdskkGo="
        ];
      };
    };
  };
}
```

## Configuration Options

### Common Settings (all roles)

- `network.interface`: The network interface for cluster communication
- `network.port`: Port for cluster communication (default: 7946)  
- `bootstrapNodes`: List of bootstrap nodes to connect to when joining
- `files`: Map of file names to lists of authorized ED25519 public keys

## Uploading Files

Once the cluster is running, you can upload files using the CLI:

```bash
# Create a file and upload it
echo "my content" > /tmp/myfile
data-mesher file update /tmp/myfile --url http://localhost:7331 --key-path /path/to/signing.key
```

Files will automatically sync to all nodes in the cluster that have the same
file definition in their configuration.
