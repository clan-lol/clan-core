# Managing Secrets with Clan

Clan enables encryption of secrets within a Clan flake, ensuring secure sharing among users.
This documentation will guide you through managing secrets with the Clan CLI,
which utilizes the [sops](https://github.com/getsops/sops) format and
integrates with [sops-nix](https://github.com/Mic92/sops-nix) on NixOS machines.

## 1. Generating Keys and Creating Secrets

To begin, generate a key pair:

```shellSession
$ clan secrets key generate
```

**Output**:

```
Public key: age1wkth7uhpkl555g40t8hjsysr20drq286netu8zptw50lmqz7j95sw2t3l7
Generated age private key at '/home/joerg/.config/sops/age/keys.txt' for your user.
Generated age private key at '/home/joerg/.config/sops/age/keys.txt' for your user. Please back it up on a secure location or you will lose access to your secrets.
Also add your age public key to the repository with 'clan secrets users add youruser age1wkth7uhpkl555g40t8hjsysr20drq286netu8zptw50lmqz7j95sw2t3l7' (replace you
user with your user name)
```

⚠️ **Important**: Backup the generated private key securely, or risk losing access to your secrets.

Next, add your public key to the Clan flake repository:

```shellSession
$ clan secrets users add <your_username> <your_public_key>
```

Doing so creates this structure in your Clan flake:

```
sops/
└── users/
    └── <your_username>/
        └── key.json
```

Now, to set your first secret:

```shellSession
$ clan secrets set mysecret
Paste your secret:
```

Note: As you type your secret, keypresses won't be displayed. Press Enter to save the secret.

Retrieve the stored secret:

```shellSession
$ clan secrets get mysecret
```

And list all secrets like this:

```shellSession
$ clan secrets list
```

Secrets in the repository follow this structure:

```
sops/
├── secrets/
│   └── <secret_name>/
│       ├── secret
│       └── users/
│           └── <your_username>/
```

The content of the secret is stored encrypted inside the `secret` file under `mysecret`.
By default, secrets are encrypted with your key to ensure readability.

## 2. Adding Machine Keys

New machines in Clan come with age keys stored in `./sops/machines/<machine_name>`. To list these machines:

```shellSession
$ clan secrets machines list
```

For existing machines, add their keys:

```shellSession
$ clan secrets machines add <machine_name> <age_key>
```

To fetch an age key from an SSH host key:

```shellSession
$ ssh-keyscan <domain_name> | nix shell nixpkgs#ssh-to-age -c ssh-to-age
```

## 3. Assigning Access

By default, secrets are encrypted for your key. To specify which users and machines can access a secret:

```shellSession
$ clan secrets set --machine <machine1> --machine <machine2> --user <user1> --user <user2> <secret_name>
```

You can add machines/users to existing secrets without modifying the secret:

```shellSession
$ clan secrets machines add-secret <machine_name> <secret_name>
```

## 4. Utilizing Groups

For convenience, Clan CLI allows group creation to simplify access management. Here's how:

1. **Creating Groups**:

   Assign users to a new group, e.g., `admins`:

   ```shellSession
   $ clan secrets groups add admins <username>
   ```

2. **Listing Groups**:

   ```shellSession
   $ clan secrets groups list
   ```

3. **Assigning Secrets to Groups**:

   ```shellSession
   $ clan secrets groups add-secret <group_name> <secret_name>
   ```

# NixOS integration

A NixOS machine will automatically import all secrets that are encrypted for the
current machine. At runtime it will use the host key to decrypt all secrets into
a in-memory, non-persistent filesystem using
[sops-nix](https://github.com/Mic92/sops-nix). In your nixos configuration you
can get a path to secrets like this `config.sops.secrets.<name>.path`. Example:

```nix
{ config, ...}: {
  sops.secrets.my-password.neededForUsers = true;

  users.users.mic92 = {
    isNormalUser = true;
    passwordFile = config.sops.secrets.my-password.path;
  };
}
```

See the [readme](https://github.com/Mic92/sops-nix) of sops-nix for more
examples.

# Importing existing sops-based keys / sops-nix

`clan secrets` stores each secrets in a single file, whereas [sops](https://github.com/Mic92/sops-nix)
commonly allows to put all secrets in a yaml or json documents.

If you already happend to use sops-nix, you can migrate by using the `clan secrets import-sops` command by importing these documents:

```shellSession
% clan secrets import-sops --prefix matchbox- --group admins --machine matchbox nixos/matchbox/secrets/secrets.yaml
```

This will create secrets for each secret found in `nixos/matchbox/secrets/secrets.yaml` in a ./sops folder of your repository.
Each member of the group `admins` will be able

Since our clan secret module will auto-import secrets that are encrypted for a particular nixos machine,
you can now remove `sops.secrets.<secrets> = { };` unless you need to specify more options for the secret like owner/group of the secret file.
