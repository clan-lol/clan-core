!!! Danger "Experimental"
    This service is experimental and will change in the future.

---

This service will set up data-mesher, a file synchronization daemon that uses a gossip protocol to replicate files 
across a cluster of nodes.

## Architecture

Data-mesher v2 uses a file-based approach where:

- Files are defined with a list of authorized public keys (ED25519)
- Only files listed in the configuration can be uploaded or synced
- Files must be signed by one of the configured public keys

## Roles

- **default**: A node that can sign files, act as a bootstrap node and distribute files to other nodes

## Usage

```nix
inventory.instances = {
  data-mesher = {
    module = {
      name = "data-mesher";
      input = "clan-core";
    };   
    roles.default.settings = {                  
      files = {
        "config_app" = [
          "azwT+VhTxA+BF73Hwq0uqdXHG8XvHU2BknoVXgmEjww="
        ];
        "shared_data" = [
          "azwT+VhTxA+BF73Hwq0uqdXHG8XvHU2BknoVXgmEjww="
          "Mdtz9s2DEyEk0DL8ZzW7WqwAehoQ97PFHVbJJdskkGo="
        ];
      };
    };
  };
}
```

## Configuration Options

- `logLevel`: Log level (default: info)
- `port`: Port for cluster communication (default: 7946)
- `extraBootstrapPeers`: List of extra bootstrap peers to connect to when joining the cluster.
- `interfaces`: The network interface(s) for cluster communication - defaults to all interfaces
- `files`: Map of file names to lists of authorized ED25519 public keys

## Uploading Files

Once the cluster is running, you can upload files using the CLI:

```bash
# Create a file and upload it
echo "my content" > /tmp/myfile
data-mesher file update /tmp/myfile --url http://localhost:7331 --key-path /path/to/signing.key
```

Files will automatically sync to all nodes in the cluster that have the same file definition in their configuration.
