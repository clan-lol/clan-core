# User Firewall Module

This NixOS module provides network access restrictions for non-privileged users, ensuring they can only access local services and VPN interfaces while blocking direct internet access.

## Overview

The `user-firewall` module implements firewall rules that:
- Block all outbound network traffic for normal (non-system) users by default
- Allow specific users to bypass restrictions (exemptUsers)
- Permit traffic on specific interfaces (like VPNs and localhost)
- Support both iptables and nftables backends
- Handle both IPv4 and IPv6 traffic

## Installation

Add the module to your NixOS configuration:

```nix
{
  imports = [
    self.inputs.clan-core.nixosModules.user-firewall
  ];
}
```

The module is automatically enabled once imported. It will immediately start restricting network access for all normal users except those listed in `exemptUsers`.

## Configuration

### Basic Usage

```nix
{
  networking.user-firewall = {
    exemptUsers = [ "alice" ];  # Users who can access the internet
  };
}
```

### Full Configuration Example

```nix
{
  networking.user-firewall = {
    # Users who are exempt from network restrictions
    exemptUsers = [
      "alice"
      "admin"
    ];

    # Network interfaces that all users can use
    # Default includes common VPN interfaces
    allowedInterfaces = [
      "lo"          # localhost (required for local services)
      "tun*"        # OpenVPN, OpenConnect
      "wg*"         # WireGuard (wg0, wg-home, etc.)
      "tailscale*"  # Tailscale
      # Add custom interfaces as needed
    ];
  };
}
```

## How It Works

1. **User Classification**: The module automatically identifies all normal users (non-system users) and applies restrictions to those not in the `exemptUsers` list.

2. **Firewall Rules**:
   - For iptables: Creates a custom chain `user-firewall-output` in the OUTPUT table
   - For nftables: Creates a table `inet user-firewall` with an output chain
   - Rules check outgoing packets and reject those from restricted users

3. **Interface Patterns**: Supports wildcards in interface names:
   - `*` matches any characters (e.g., `wg*` matches `wg0`, `wg-home`)

## Default Allowed Interfaces

The module comes with sensible defaults for common VPN and overlay network interfaces:

- `lo` - Loopback (localhost access)
- `tun*` - OpenVPN, OpenConnect
- `tap*` - OpenVPN (bridged mode)
- `wg*` - WireGuard
- `tailscale*` - Tailscale
- `zt*` - ZeroTier
- `hyprspace` - Hyprpspace
- `vpn*` - Generic VPN interfaces
- `nebula*` - Nebula mesh network
- `tinc*` - Tinc VPN
- `edge*` - n2n
- `ham0` - Hamachi
- `easytier` - EasyTier
- `mycelium` - Mycelium

## Use Cases

### 1. Public Kiosk Systems
Restrict users to only access local services:
```nix
{
  networking.user-firewall = {
    allowedInterfaces = [ "lo" ];  # Only localhost
    exemptUsers = [ ];  # No exempt users
  };
}
```

### 2. Corporate Workstations
Force all traffic through corporate VPN:
```nix
{
  networking.user-firewall = {
    allowedInterfaces = [ "lo" "wg-corp" ];
    exemptUsers = [ "sysadmin" ];
  };
}
```

## Testing

The module includes comprehensive tests for both iptables and nftables backends:

```bash
# Run iptables backend test
nix build .#checks.x86_64-linux.user-firewall-iptables

# Run nftables backend test
nix build .#checks.x86_64-linux.user-firewall-nftables
```

## Troubleshooting

### Check Active Rules

The output includes package counters for each firewall rule, that can help to debug connectivity issues.

For iptables:
```bash
sudo iptables -L user-firewall-output -n -v
sudo ip6tables -L user-firewall-output -n -v
```

For nftables:
```bash
sudo nft list table inet user-firewall

# Watch counters in real-time
sudo watch -n1 'nft list table inet user-firewall'
```

Check which rule your VPN traffic is hitting. If packets are being rejected, verify:
1. Your VPN interface name matches the patterns in `allowedInterfaces`
2. Your user is listed in `exemptUsers` if needed

To see your current network interfaces:
```bash
ip link show | grep -E '^[0-9]+:'
```

### Common Issues

1. **Service Connection Failures**: If local services fail to connect, ensure `lo` is in `allowedInterfaces`.

2. **VPN Not Working**: Check that your VPN interface name matches the patterns in `allowedInterfaces`. You can find your interface name with `ip link show`.

3. **User Still Has Access**: Verify the user is a normal user (not a system user) and not in `exemptUsers`.

## Security Considerations

- This module provides defense in depth but should not be the only security measure
- System users (like `nginx`, `systemd-*`) are not restricted
- Root user always has full network access
- Restrictions apply at the packet filter level, not application level

## Limitations

- Requires `networking.firewall.enable = true`
- Cannot restrict system users or root
- Interface patterns are evaluated at rule creation time, not dynamically
