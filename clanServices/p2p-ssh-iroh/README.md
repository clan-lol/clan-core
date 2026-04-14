:::admonition[Experimental]{type=danger}
This service is experimental and will change in the future.

:::

SSH over [dumbpipe](https://github.com/n0-computer/dumbpipe) (iroh) — NAT-traversing SSH access via encrypted QUIC streams.

## Overview

This service enables SSH access to machines behind NAT or firewalls without port forwarding, using iroh's peer-to-peer networking for NAT traversal.

By adding this service to your machines, `clan ssh <machine>` will work from any admin machine — even if the admin is not within the clan's VPN or on the same network. Iroh handles peer discovery and NAT traversal automatically, falling back to relay servers when a direct connection cannot be established.

The **server** role exposes the machine's sshd via a dumbpipe listener, generating a stable iroh identity and a connection ticket. The ticket is exported so the clan networking abstraction can use it for connectivity.

:::admonition[Security Notice]{type=warning}
Enabling this service exposes the machine's SSH service to **anyone on the iroh network**. The only protection against unauthorized access is SSH authentication itself. Make sure all machines with this service have SSH access configured securely — use **private key authentication only** and disable password login.
:::

## Roles

### Server

- Generates an iroh secret key for a stable node identity
- Produces a connection ticket that is exported for peer discovery
- Runs a systemd service that forwards iroh connections to the local sshd
- Enables openssh automatically

## Example

```nix
{
  instances.my-tunnel = {
    module.name = "p2p-ssh-iroh";
    roles.server.machines.myserver = { };
  };
}
```
