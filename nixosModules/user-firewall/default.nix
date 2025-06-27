{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.networking.user-firewall;

  # Get all normal users (excluding system users)
  normalUsers = lib.filterAttrs (_name: user: user.isNormalUser) config.users.users;

  # Get usernames for normal users who aren't exempt
  restrictedUsers = lib.attrNames (
    lib.filterAttrs (name: _user: !(lib.elem name cfg.exemptUsers)) normalUsers
  );

  # Convert interface patterns for iptables
  # iptables uses + for one-or-more, but we use * in our interface
  toIptablesPattern =
    pattern:
    if lib.hasSuffix "*" pattern && pattern != "*" then
      # Convert "wg*" to "wg+" for iptables
      lib.removeSuffix "*" pattern + "+"
    else
      pattern;

  # Build interface patterns for iptables with proper escaping
  interfaceRules = lib.concatMapStringsSep "\n    " (
    iface:
    "ip46tables -A user-firewall-output -o ${lib.escapeShellArg (toIptablesPattern iface)} -j RETURN"
  ) cfg.allowedInterfaces;

in
{
  options.networking.user-firewall = {
    allowedInterfaces = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [
        "lo" # loopback (allows Tor on localhost)
        "tun*" # OpenVPN, OpenConnect
        "tap*" # OpenVPN (bridged mode)
        "wg*" # WireGuard (wg0, wg-home, etc.)
        "tailscale*" # Tailscale
        "zt*" # ZeroTier
        "vpn*" # Generic VPN interfaces
        "ipsec*" # IPSec
        "nebula*" # Nebula
        "tinc*" # Tinc
        "edge*" # n2n
        "hyprspace" # Hyprspace
        "ham0" # Hamachi
        "easytier" # EasyTier
        "mycelium" # Mycelium
      ];
      description = ''
        Network interfaces that normal users can use.
        Supports wildcards: * (zero or more characters).
      '';
    };

    exemptUsers = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      description = ''
        Users exempt from network restrictions.
      '';
    };

  };

  config = {
    assertions = [
      {
        assertion = config.networking.firewall.enable;
        message = "networking.user-firewall requires networking.firewall.enable to be true";
      }
    ];

    # For nftables: create fake passwd file for build-time validation
    networking.nftables.checkRulesetRedirects = lib.mkIf config.networking.nftables.enable (
      lib.mkOptionDefault {
        "/etc/passwd" = pkgs.writeText "passwd" (
          let
            userList = lib.attrNames config.users.users;
            indexedUsers = lib.imap0 (
              i: name: "${name}:x:${toString (1000 + i)}:100::/home/${name}:/bin/sh"
            ) userList;
          in
          lib.concatStringsSep "\n" indexedUsers
        );
      }
    );

    # For iptables backend
    networking.firewall.extraCommands = lib.mkIf (!config.networking.nftables.enable) ''
      # Create custom chain for user firewall output
      ip46tables -N user-firewall-output 2>/dev/null || true
      ip46tables -F user-firewall-output

      # Allow traffic on permitted interfaces
      ${interfaceRules}


      # Reject traffic from restricted users (TCP RST for TCP, ICMP for UDP)
      ${lib.concatMapStringsSep "\n      " (
        user: "ip46tables -A user-firewall-output -m owner --uid-owner ${lib.escapeShellArg user} -j REJECT"
      ) restrictedUsers}

      # Allow all other traffic
      ip46tables -A user-firewall-output -j RETURN

      # Insert our chain at the beginning of OUTPUT
      ip46tables -D OUTPUT -j user-firewall-output 2>/dev/null || true
      ip46tables -I OUTPUT -j user-firewall-output
    '';

    networking.firewall.extraStopCommands = lib.mkIf (!config.networking.nftables.enable) ''
      # Remove our custom chain
      ip46tables -D OUTPUT -j user-firewall-output 2>/dev/null || true
      ip46tables -F user-firewall-output 2>/dev/null || true
      ip46tables -X user-firewall-output 2>/dev/null || true
    '';

    # For nftables backend
    networking.nftables.tables = lib.mkIf config.networking.nftables.enable {
      user-firewall = {
        family = "inet";
        content = ''
          chain output {
            type filter hook output priority 0; policy accept;

            # Allow traffic on permitted interfaces
            ${lib.concatMapStringsSep "\n            " (
              iface: ''oifname "${iface}" counter accept comment "allow ${iface}"''
            ) cfg.allowedInterfaces}

            # Reject traffic from restricted users (TCP RST for TCP, ICMP for UDP)
            ${lib.concatMapStringsSep "\n            " (
              user: ''meta skuid "${user}" counter reject comment "blocked user ${user}"''
            ) restrictedUsers}
          }
        '';
      };
    };
  };
}
