# Introduction to Clan Vars

## 🚧 Early Notes Draft — Not Ready for Review, but okay to glance at for technical mistakes

Vars are Clan's system for managing secrets and generated values. This includes things like passwords, SSH keys, WiFi credentials, and encryption keys. They're generated on your setup machine, stored encrypted, and automatically deployed to your target machines as needed.

## The Problem Vars Solves

Without Clan, you'd have to:

1. Manually create passwords and keys
2. Copy them to each machine
3. Remember where you put them
4. Hope you don't lose them

With Clan vars:

1. Run `clan vars generate`
2. Done! Secrets are created, encrypted, and deployed automatically

## Your First Var: The Root Password

When you create a clan with the default template, it includes a root password service:

```nix
inventory.instances = {
  user-root = {
    module.name = "users";
    roles.default.tags.all = {};
    roles.default.settings = {
      user = "root";
      prompt = true;
    };
  };
};
```

When you run:

```bash
clan vars generate test-machine --no-sandbox
```

clan will scan your current vars, see that there's a need for a root password, and then prompt you for a root password (or generates one automatically if you leave it blank).

If you run the same command a second time, clan will see there's already a password created, and simply exit with no output.

## Viewing Your Vars

To see what vars exist for a machine:

```bash
clan vars list test-machine
```

Output looks similar to:

```
user-password-root/user-password-hash ********
user-password-root/user-password ********
openssh/ssh.id_ed25519.pub ssh-ed25519 AAAA...
```

Secret values are hidden with `********`.

## Retrieving a Secret

To see the actual value of a secret:

```bash
clan vars get test-machine user-password-root/user-password
```

This decrpts and displays the root password. This is useful when you need to log in to a machine's console.

## How Vars Are Stored

Vars are stored in your clan's `vars/` directory:

```
vars/
├── per-machine/
│   └── test-machine/
│       ├── user-password-root/
│       │   ├── user-password/secret       # Encrypted password
│       │   └── user-password-hash/secret  # Encrypted hash
│       └── openssh/
│           ├── ssh.id_ed25519/secret      # Encrypted private key
│           └── ssh.id_ed25519.pub/value   # Public key (not secret)
└── shared/
    └── wifi.home/
        ├── network-name/secret            # Encrypted SSID
        └── password/secret                # Encrypted password
```

- **Secret vars** are encrypted using age/SOPS
- **Public vars** (like public keys) are stored in plain text
- **Per-machine vars** are specific to one machine
- **Shared vars** are used by multiple machines

## The Vars Workflow

```
1. Add a service to clan.nix
         ↓
2. Run: clan vars generate test-machine --no-sandbox
         ↓
3. Answer any prompts (or let Clan auto-generate)
         ↓
4. Secrets are encrypted and saved to vars/
         ↓
5. Run: clan machines update test-machine
         ↓
6. Secrets are decrypted and deployed to the target
```

## Common Vars Commands

| Command | What It Does |
|---------|--------------|
| `clan vars generate <machine>` | Generate all missing vars |
| `clan vars generate <machine> --regenerate` | Regenerate all vars (even existing ones) |
| `clan vars list <machine>` | List all vars for a machine |
| `clan vars get <machine> <var-id>` | Show a specific var's value |

## The Age Key

Vars are encrypted with an age key stored at:

```
~/.config/sops/age/keys.txt
```

This key is created automatically the first time you run `clan vars generate`.

**Important:** Back up this key! If you lose it, you can't decrypt your vars.

## Example: WiFi Credentials

The WiFi service uses vars to store network credentials:

```nix
inventory.instances = {
  wifi = {
    roles.default.machines."test-machine" = {
      settings.networks.home = {};
    };
  };
};
```

When you run `clan vars generate`:

Clan again scans your clan.nix file and sees there's a need for another key. It will  prompt you for the value for wifi.home/network-name for machines: test-machine
Network SSID: MyHomeNetwork

```
Prompting value for wifi.home/network-name for machines: test-machine
name of the Wi-Fi network: MyNetwork
Enter the value for wifi.home/password: (hidden): ****
Confirm Enter the value for wifi.home/password: (hidden): ****
```

These are encrypted and stored. When you deploy, they're decrypted on the target machine and configured in NetworkManager.

## Example: SSH Host Keys

The `sshd` service automatically generates SSH host keys:

```nix
inventory.instances = {
  sshd = {
    roles.server.tags.all = {};
  };
};
```

Run `clan vars generate` and it creates:

- `openssh/ssh.id_ed25519` -- Private host key (secret)
- `openssh/ssh.id_ed25519.pub` -- Public host key (not secret)

No prompts are needed; the keys are generated automatically.

## Regenerating Vars

If you need to change a passwrd or regenerate keys:

```bash
# Regenerate a specific generator
clan vars generate test-machine --generator user-password-root --regenerate

# Regenerate everything
clan vars generate test-machine --regenerate
```

Then deploy:

```bash
clan machines update test-machine
```


## How Vars Connect to Services

Services defne what vars they need. For example, the `users` service defines:

- A prompt for the password
- A script that hashes the password
- Output files for the hash

You don't need to know the details. Just run `clan vars generate` and answer the prompts. The service handles the rest.
