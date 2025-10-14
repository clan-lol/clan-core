
## What it does
- Generates and persists SSH host keys via `vars`.
- Optionally issues CA-signed host certificates for servers.
- Installs the `server` CA public key into `clients` `known_hosts` for TOFU-less verification.


## When to use it
- Zero-TOFU SSH for dynamic fleets: admins/CI can connect to frequently rebuilt hosts (e.g., server-1.example.com) without prompts or per-host `known_hosts` churn.

### Roles
- Server: runs sshd, presents a CA-signed host certificate for `<machine>.<domain>`.
- Client: trusts the CA for the given domains to verify servers' certificates.
  Tip: assign both roles to a machine if it should both present a cert and verify others.

Quick start (with host certificates)
Useful if you never want to get a prompt about trusting the ssh fingerprint.
```nix
{
  inventory.instances = {
    sshd-with-certs = {
      module = { name = "sshd"; input = "clan-core"; };
      # Servers present certificates for <machine>.example.com
      roles.server.tags.all = { };
      roles.server.settings = {
        certificate.searchDomains = [ "example.com" ];
        # Optional: also add RSA host keys
        # hostKeys.rsa.enable = true;
      };
      # Clients trust the CA for *.example.com
      roles.client.tags.all = { };
      roles.client.settings = {
        certificate.searchDomains = [ "example.com" ];
      };
    };
  };
}
```

Basic: only add persistent host keys (ed25519), no certificates
Useful if you want to get an ssh "trust this server" prompt once and then never again. 
```nix
{
  inventory.instances = {
    sshd-basic = {
      module = {
        name = "sshd";
        input = "clan-core";
      };
      roles.server.tags.all = { };
    };
  };
}
```

Example: selective trust per environment
Admins should trust only production; CI should trust prod and staging. Servers are reachable under both domains.
```nix
{
  inventory.instances = {
    sshd-env-scoped = {
      module = { name = "sshd"; input = "clan-core"; };

      # Servers present certs for both prod and staging FQDNs
      roles.server.tags.all = { };
      roles.server.settings = {
        certificate.searchDomains = [ "prod.example.com" "staging.example.com" ];
      };

      # Admin laptop: trust prod only
      roles.client.machines."admin-laptop".settings = {
        certificate.searchDomains = [ "prod.example.com" ];
      };

      # CI runner: trust prod and staging
      roles.client.machines."ci-runner-1".settings = {
        certificate.searchDomains = [ "prod.example.com" "staging.example.com" ];
      };
    };
  };
}
```
### Explanation
- Admin -> server1.prod.example.com: zero-TOFU (verified via cert).
- Admin -> server1.staging.example.com: falls back to TOFU (or is blocked by policy).
- CI -> either prod or staging: zero-TOFU for both.
Note: server and client searchDomains don't have to be identical; they only need to overlap for the hostnames you actually use.

### Notes
- Connect using a name that matches a cert principal (e.g., `server1.example.com`); wildcards are not allowed inside the certificate.
- CA private key stays in `vars` (not deployed); only the CA public key is distributed.
- Logins still require your user SSH keys on the server (passwords are disabled).