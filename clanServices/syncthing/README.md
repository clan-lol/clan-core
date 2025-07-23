# Syncthing Service

This service provides automatic Syncthing peer discovery and configuration for clan machines.

## Features

- Automatic peer discovery across all clan machines
- Integration with ZeroTier for reliable connectivity
- Configurable firewall rules for Syncthing ports
- Certificate and key management through clan vars
- Folder synchronization configuration

## Usage

```nix
{
  services.syncthing = {
    instances.default = {
      # Configure folders and external devices for all peers
      roles.peer.settings = {
        extraDevices = {
          phone = {
            id = "P56IOI7-MZJNU2Y-IQGDREY-DM2MGTI-MGL3BXN-PQ6W5BM-TBBZ4TJ-XZWICQ2";
            name = "My Phone";
            addresses = [ "dynamic" ];
          };
          tablet = {
            id = "A12BC34-DEFG567-HIJK890-LMNO123-PQRS456-TUVW789-XYZA012-BCDE345";
            name = "Family Tablet";
          };
        };
        
        folders = {
          shared-docs = {
            path = "/home/shared/documents";
            type = "sendreceive";
          };
          backup = {
            path = "/home/backup";
            type = "sendonly";
            devices = [ "machine1" "machine2" ]; # Only share with specific machines
            versioning = {
              type = "simple";
              params.keep = "10";
            };
          };
          photos = {
            path = "/home/photos";
            devices = [ "phone" "tablet" ]; # Only share with mobile devices
            type = "receiveonly";
          };
        };
      };
      
      # Per-machine configuration
      roles.peer.machines = {
        machine1 = {
          folders = {
            machine1-only = {
              path = "/home/user/private";
              type = "sendonly";
            };
          };
        };
        machine2 = {
          openDefaultPorts = false; # Disable firewall rules
          folders = {
            machine2-photos = {
              path = "/home/user/Pictures";
              type = "receiveonly";
            };
          };
        };
      };
    };
  };
}
```

## Configuration Options

### `openDefaultPorts`
- **Type**: `bool`
- **Default**: `true`
- **Description**: Whether to open the default syncthing ports in the firewall

### `extraDevices`
- **Type**: `attrsOf (submodule)`
- **Default**: `{}`
- **Description**: External syncthing devices not managed by clan (e.g., mobile phones)

#### Extra Device Options
- `id` (str): Device ID of the external syncthing device
- `name` (str): Human readable name for the device (defaults to device key name)
- `addresses` (listOf str): List of addresses for the device (default: ["dynamic"])

### `folders`
- **Type**: `attrsOf (submodule)`
- **Default**: `{}`
- **Description**: Folders to synchronize between peers

#### Folder Options
- `path` (str): Path to the folder to sync
- `devices` (listOf str): List of device names to share this folder with. Empty list means all peers and extraDevices (default: [])
- `type` (enum): Folder type - "sendreceive", "sendonly", or "receiveonly" (default: "sendreceive")
- `ignorePerms` (bool): Ignore permission changes (default: false)
- `rescanIntervalS` (int): Rescan interval in seconds (default: 3600)
- `versioning` (submodule, optional): Versioning configuration
  - `type` (enum): "external", "simple", "staggered", or "trashcan"
  - `params` (attrs): Versioning parameters

## Network Requirements

When `openDefaultPorts` is true, this service opens the following firewall ports:
- TCP 8384: Syncthing web GUI (on ZeroTier interfaces and public)
- TCP/UDP 22000: Syncthing sync traffic (on ZeroTier interfaces)
- UDP 21027: Syncthing discovery (on ZeroTier interfaces)

## ZeroTier Integration

When machines have ZeroTier configured, the service automatically adds ZeroTier IP addresses as preferred connection addresses for more reliable peer-to-peer communication.

## Generated Variables

The service generates the following variables for each machine:
- `syncthing/key`: Private key for TLS
- `syncthing/cert`: Certificate for TLS
- `syncthing/api`: API key for web interface
- `syncthing/id`: Device identifier (public)