# age Backend for Vars

The **age** backend encrypts secrets using [age](https://github.com/FiloSottile/age) and decrypts them on the target machine during NixOS activation. Secrets are stored encrypted in your repository and uploaded encrypted to target machines — plaintext only exists in memory on the target.

## When to Use the Age Backend

Choose the age backend when:

- You want **simple, direct age encryption** without sops
- You want **target-side decryption** without the sops-nix Go binary
- You want automatic machine key management
- Your identity is a hardware token (YubiKey, PicoHSM) via age plugins

Choose the [SOPS backend](../sops/secrets) when:

- You already use sops in your workflow
- You need sops-nix's systemd service integration

## How It Works

The age backend uses **machine keypairs** with key indirection:

1. Each machine gets an age keypair. The private key is encrypted to your user key(s).
2. Secrets are encrypted to machine public keys (not directly to user keys).
3. During deployment, the machine's decrypted private key and encrypted secrets are uploaded.
4. On boot, NixOS activation scripts decrypt secrets using the machine key.

This means **user key rotation** only re-encrypts machine keys (one per machine), not every secret. Shared secrets are encrypted to all machines' public keys using age's native multi-recipient support.

## Quick Start

### 1. Set Up Your Age Identity

The backend automatically checks these locations for your private key:

1. `AGE_KEY` environment variable (key content)
2. `AGE_KEYFILE` environment variable (path to key file)
3. `~/.config/age/identities`
4. `~/.config/sops/age/keys.txt`
5. `~/.age/key.txt`

If you don't have a key yet:

```bash
mkdir -p ~/.config/age
age-keygen -o ~/.config/age/identities
```

Note the public key from the output — you'll need it below.

:::admonition[Tip]{type=tip}
Hardware tokens (YubiKey, PicoHSM) work via age plugin identity files placed at any of the paths above.
:::

### 2. Configure the Age Backend

In your `clan.nix`:

```nix
{
  # Select the age backend
  vars.settings.secretStore = "age";

  # Your public key(s) as default recipients for all machines
  vars.settings.recipients.default = [
    "age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p"
  ];

  # Optionally override recipients for specific machines
  # vars.settings.recipients.hosts.my-machine = [
  #   "age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p"
  #   "age1another..."
  # ];
}
```

### 3. Generate Secrets

```bash
clan vars generate my-machine
```

This will:

1. Auto-generate a machine keypair (if not already present)
2. Encrypt the machine's private key to your recipient key(s)
3. Run generators and encrypt their secret outputs to the machine's public key
4. Commit everything to the repository

### 4. Deploy

```bash
clan machines update my-machine
```

The backend uploads encrypted secrets to the target, where NixOS activation scripts decrypt them on boot.

## Decryption Phases

Secrets are decrypted at different points during NixOS activation, controlled by the `neededFor` option on each secret file:

| Phase | Decrypted to | When | Use case |
|-------|-------------|------|----------|
| `users` | `/run/user-secrets/` (tmpfs) | Before user/group creation | Secrets needed by user definitions (e.g., `hashedPasswordFile`) |
| `services` | `/run/secrets/` (tmpfs) | After users exist | Service credentials, API keys |
| `activation` | In-place at upload location | During activation | Secrets for other activation scripts |
| `partitioning` | `/run/partitioning-secrets/` (tmpfs) | During partitioning | Disk encryption keys |

Secrets on tmpfs never touch disk and are lost on reboot (re-decrypted on next boot).

## Configuration Reference

### `vars.settings.secretStore`

Set to `"age"` to use the age backend:

```nix
vars.settings.secretStore = "age";
```

### `vars.settings.recipients.hosts.<machine>`

List of age public keys that can decrypt the machine's private key. Typically your admin key(s):

```nix
vars.settings.recipients.hosts.webserver = [
  "age1admin1..."
  "age1admin2..."  # Multiple admins
];
```

### `vars.settings.recipients.default`

Fallback recipients used when no host-specific recipients are configured:

```nix
vars.settings.recipients.default = [
  "age1admin..."
];
```

:::admonition[Note]{type=note}
Default recipients are only used if `recipients.hosts.<machine>` is **not** set. They do not combine with host-specific recipients.
:::

### `clan.core.vars.age.secretLocation`

Location on the target where encrypted secrets are uploaded (default: `/etc/secret-vars`):

```nix
clan.core.vars.age.secretLocation = "/etc/my-secrets";
```

### `vars.settings.age.externalStore`

Keep the age store outside the flake repository (default: `false`), see
[External Store](#external-store-public-repositories):

```nix
vars.settings.age.externalStore = true;
```

## Repository Layout

```text
your-clan/
├── clan.nix
├── secrets/
│   ├── age-keys/
│   │   └── machines/
│   │       └── my-machine/
│   │           ├── pub          # Machine public key (plaintext)
│   │           └── key.age      # Machine private key (encrypted to user keys)
│   └── clan-vars/
│       ├── per-machine/
│       │   └── my-machine/
│       │       └── openssh/
│       │           └── ssh.id_ed25519.age
│       └── shared/
│           └── cluster-token/
│               └── token.age
└── vars/
    └── per-machine/
        └── my-machine/
            └── openssh/
                └── ssh.id_ed25519.pub/
                    └── value     # Public (non-secret) values
```

## External Store (Public Repositories)

By default the `secrets/` store is committed to the flake repository. For a
public flake repository this permanently publishes the (encrypted) secrets
with their full git history. To keep the store out of the flake entirely:

```nix
# clan.nix — commits the intent, not the location
vars.settings.age.externalStore = true;
```

```bash
# each admin's environment — their local copy of the store
export CLAN_AGE_STORE_DIR=~/clan-secrets
```

The flag is a boolean on purpose: admins managing shared infrastructure can
keep their store copies in different places. If `CLAN_AGE_STORE_DIR` points
to a git repository, clan commits store changes there with the same commit
messages it would use in the flake repo — share it out-of-band like a
passage/password-store repository.

Migrating an existing in-repo store:

```bash
mv secrets "$CLAN_AGE_STORE_DIR"
git rm -r --cached secrets && git commit
```

The encrypted secrets remain in the flake's git history until it is
rewritten.

Misconfigurations fail loudly: enabling the flag without the environment
variable, setting the variable without the flag, pointing it inside the
flake repository, or leaving a non-empty `secrets/` behind are all errors.

### Deployment implications

With an internal store the encrypted secrets are part of the system closure.
With an external store they are not: `clan machines update` uploads them to
`secretLocation` alongside the machine key, and activation decrypts them
from there. Two consequences:

- Building system closures (CI, `nix build`, `nix flake check`) requires no
  access to the store at all.
- Activating a system without a prior `clan machines update` — a bare
  `nixos-rebuild switch`, or rolling back to an old generation after secrets
  changed — can leave secrets missing; activation prints a
  `not found, skipping` warning for each.

## Multiple Recipients

Multiple recipients can all decrypt a machine's private key. This is useful for team access:

```nix
{
  vars.settings.recipients.hosts.production = [
    "age1admin1..." # Primary admin
    "age1admin2..." # Backup admin
    "age1cikey..." # CI/CD system
  ];
}
```

All listed recipients can run `clan vars generate` and `clan machines update` for that machine.

## Key Rotation

### Rotating user keys

When admin keys change, re-encrypt machine private keys to the new recipients:

```bash
# Update recipients in clan.nix, then:
clan vars fix my-machine
```

This decrypts each machine key with the old identity and re-encrypts to the new recipients. Secrets themselves don't need re-encryption.

### Adding/removing machines

When machines are added or removed, shared secrets are automatically re-encrypted to include/exclude the machine's public key during `clan vars generate`.

## Health Checks

```bash
clan vars check my-machine
```

Verifies:

- Recipients are configured for the machine
- An age identity is available for decryption

## Troubleshooting

### "No age recipients configured for machine"

Set recipients in `clan.nix`:

```nix
vars.settings.recipients.hosts.my-machine = [ "age1..." ];
```

### "No age identity found"

Place your age private key at one of the well-known paths, or set an environment variable:

```bash
# File-based
export AGE_KEYFILE=~/.config/age/identities

# Or inline
export AGE_KEY="AGE-SECRET-KEY-1..."
```

### "AGE_KEYFILE points to non-existent file"

Check the path in `AGE_KEYFILE` exists and is readable.

## Comparison with SOPS Backend

| Feature | Age Backend | SOPS Backend |
|---------|-------------|--------------|
| Encryption tool | age directly | sops (wrapping age) |
| Decryption location | Target machine (activation scripts) | Target machine (sops-nix) |
| Decryption binary | `age` (shell scripts) | `sops-install-secrets` (Go) |
| Machine keys | Auto-generated, in-repo or external store | Auto-generated, in-repo |
| Key indirection | Yes (user → machine key → secret) | Yes (similar) |
| Shared secrets | Multi-recipient age encryption | sops-nix groups |
| Hardware tokens | Via age plugins | Via sops/age plugins |

## See Also

- [Age encryption tool](https://github.com/FiloSottile/age)
- [Introduction to Vars](../intro-to-vars)
- [SOPS Backend](../sops/secrets)
