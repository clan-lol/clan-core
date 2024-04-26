## Secrets (CLI Reference)

#### Adding Secrets (set)

```bash
clan secrets set mysecret
> Paste your secret: 
```

!!! note
    As you type your secret won't be displayed. Press Enter to save the secret.

#### List all Secrets (list)

```bash
clan secrets list
```

#### Assigning Access (set)

By default, secrets are encrypted for your key. To specify which users and machines can access a secret:

```bash
clan secrets set --machine <machine1> --machine <machine2> --user <user1> --user <user2> <secret_name>
```

#### Displaying Secrets (get)

```bash
clan secrets get mysecret
```

#### Rename

TODO

#### Remove

TODO

#### import-sops

TODO

### Users (Reference)

Learn how to manage users and allowing access to existing secrets.

#### list user

Lists all added users

```bash
clan secrets user list
```

``` {.console, title="Example output", .no-copy}
jon
sara
```

!!! Question "Who can execute this command?"
    Everyone - completely public.

#### add user

add a user

```bash
clan secrets users add {username} {public-key}
```

!!! Note
    Changes can be trusted by maintainer review in version control.

#### get user

get a user public key

```bash
clan secrets users get {username}
```

``` {.console, title="Example output", .no-copy}
age1zk8uzrte55wkg9lkqxu5x6twsj2ja4lehegks0cw4mkg6jv37d9qsjpt44
```

#### remove user

remove a user

```bash
clan secrets users remove {username}
```

!!! Note
    Changes can be trusted by maintainer review in version control.

#### add-secret user

Grants the user (`username`) access to the secret (`secret_name`)

```bash
clan secrets users add-secret {username} {secret_name}
```

!!! Note
    Requires the executor of the command to have access to the secret (`secret_name`).

#### remove-secret user

remove the user (`username`) from accessing the secret (`secret_name`)

!!! Danger "Make sure at least one person has access."
    It might still be possible for the machine to access the secret. (See [machines](#machines))

    We highly recommend to use version control such as `git` which allows you to rollback secrets in case anything gets messed up.

```bash
clan secrets users remove-secret {username} {secret_name}
```

!!! Question "Who can execute this command?"
    Requires the executor of the command to have access to the secret (`secret_name`).

### Machines (Reference)

- [list](): list machines
- [add](): add a machine
- [get](): get a machine public key
- [remove](): remove a machine
- [add-secret](): allow a machine to access a secret
- [remove-secret](): remove a machine's access to a secret

#### List machine

New machines in Clan come with age keys stored in `./sops/machines/<machine_name>`. To list these machines:

```bash
clan secrets machines list
```

#### Add machine

For clan machines the machine key is generated automatically on demand if none exists.

```bash
clan secrets machines add <machine_name> <age_key>
```

If you already have a device key and want to add it manually, see: [How to obtain a remote key](#obtain-remote-keys-manually)

#### get machine

TODO

#### remove machine

TODO

#### add-secret machine

TODO

#### remove-secret machine

TODO

### Groups (Reference)

The Clan-CLI makes it easy to manage access by allowing you to create groups.

- [list](): list groups
- [add-user](): add a user to group
- [remove-user](): remove a user from group
- [add-machine](): add a machine to group
- [remove-machine](): remove a machine from group
- [add-secret](): allow a user to access a secret
- [remove-secret](): remove a group's access to a secret

#### List Groups

```bash
clan secrets groups list
```

#### add-user

Assign users to a new group, e.g., `admins`:

```bash
clan secrets groups add-user admins <username>
```

!!! info
    The group is created if no such group existed before.

    The user must exist in beforehand (See: [users](#users-reference))

    ```{.console, .no-copy}
    .
    ├── flake.nix
    .   ...
    └── sops
        ├── groups
        │   └── admins
        │       └── users
        │           └── <username> -> ../../../users/<username>
    ```

#### remove-user

TODO

#### add-machine

TODO

#### remove-machine

TODO

#### add-secret

```bash
clan secrets groups add-secret <group_name> <secret_name>
```

#### remove-secret

TODO

### Key (Reference)

- [generate]() generate age key
- [show]() show age public key
- [update]() re-encrypt all secrets with current keys (useful when changing keys)

#### generate

TODO

#### show

TODO

#### update

TODO

## Further

Secrets in the repository follow this structure:

```{.console, .no-copy}
sops/
├── secrets/
│   └── <secret_name>/
│       ├── secret
│       └── users/
│           └── <your_username>/
```

The content of the secret is stored encrypted inside the `secret` file under `mysecret`.

By default, secrets are encrypted with your key to ensure readability.

### Obtain remote keys manually

To fetch a **SSH host key** from a preinstalled system:

```bash
ssh-keyscan <domain_name> | nix shell nixpkgs#ssh-to-age -c ssh-to-age
```

!!! Success
    This command converts the SSH key into an age key on the fly. Since this is the format used by the clan secrets backend.

    Once added the **SSH host key** enables seamless integration of existing machines with clan.

Then add the key by executing:

```bash
clan secrets machines add <machine_name> <age_key>
```

See also: [Machine reference](#machines-reference)

### NixOS integration

A NixOS machine will automatically import all secrets that are encrypted for the
current machine. At runtime it will use the host key to decrypt all secrets into
an in-memory, non-persistent filesystem using [sops-nix](https://github.com/Mic92/sops-nix). 
In your nixos configuration you can get a path to secrets like this `config.sops.secrets.<name>.path`. For example:

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

### Migration: Importing existing sops-based keys / sops-nix

`clan secrets` stores each secret in a single file, whereas [sops](https://github.com/Mic92/sops-nix) commonly allows to put all secrets in a yaml or json document.

If you already happened to use sops-nix, you can migrate by using the `clan secrets import-sops` command by importing these files:

```bash
% clan secrets import-sops --prefix matchbox- --group admins --machine matchbox nixos/matchbox/secrets/secrets.yaml
```

This will create secrets for each secret found in `nixos/matchbox/secrets/secrets.yaml` in a `./sops` folder of your repository.
Each member of the group `admins` in this case will be able to decrypt the secrets with their respective key.

Since our clan secret module will auto-import secrets that are encrypted for a particular nixos machine,
you can now remove `sops.secrets.<secrets> = { };` unless you need to specify more options for the secret like owner/group of the secret file.
