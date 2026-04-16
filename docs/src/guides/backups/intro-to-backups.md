# Introduction to Backups

Clan makes it easy to back your machines up from one to another. You define what to back up and where to send it, and Clan handles the rest: encryption, scheduling, and restoration.

## How Clan Backups Work

Clan backups have two parts:

1. **What to back up**: folders, databases, application state
2. **Where to send it**: another machine in your clan, or a remote location such as a Hetzner storage box.

Under the hood, Clan uses [BorgBackup](https://www.borgbackup.org/), which provides:

- **Deduplication**: If two identical files are backed up, they only occupy a single set of data on the backup server
- **Encryption**: backups are encrypted before leaving the machine
- **Compression**: smaller backups, faster transfers

You don't need to know BorgBackup to use Clan backups. Clan handles everything for you.

## The Basic Setup

The borgbackup service has two roles:

| Role | What it does |
|------|--------------|
| **client** | Creates backups and sends them to the server |
| **server** | Receives and stores backups from clients |

A machine can be both. For example, a NAS might store backups from your laptops (server role) while also backing itself up to an offsite location (client role).

On each client machine, you define a **state** — the folders and data to include in backups. This goes in the clan.nix file's `machines` attribute, as you'll see in the following example.

You also define a backup server where backups will be stored.

**Why "state" instead of "backup"?** The `clan.core.state` option declares "this data is important". It's not specific to backups. The backup service reads your state definitions and includes them automatically. This separation means you define what matters once, and different services (backup, restore, migration) can all use it. If you ever switch backup tools, your state definitions stay the same.

## Starting Example

This step-by-step example demonstrates how to set up and use backups.

Start two machines under a single clan. If you're using VirtualBox or a cloud server, we suggest naming them `alice-laptop` and `backup-server`. Note the IP address of each machine.

Replace the contents of your `clan.nix` file with the following. Update `meta.name` and `meta.domain` to your chosen values, replace the IP addresses for both machines, and paste your SSH public key in the two places indicated.

```nix
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "MY-BACKUP-CLAN";
  meta.domain = "mybackupclan.lol";

  inventory.machines = {
    alice-laptop = {
      deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH ALICE'S IP ADDRESS; keep "root@"
      tags = [ ];
    };
    backup-server = {
      deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH BACKUP'S IP ADDRESS; keep "root@"
      tags = [ ];
    };

  };

  # Docs: See https://docs.clan.lol/latest/services/definition/
  inventory.instances = {
    borgbackup = {
      roles.client.machines."alice-laptop" = { };
      roles.server.machines."backup-server" = {
        settings.address = "<IP-ADDRESS>"; # REPLACE WITH BACKUP'S IP ADDRESS
        settings.directory = "/var/lib/borgbackup";
      };
    };

    user-alice = {
      module.name = "users";
      roles.default.machines."alice-laptop" = { };
      roles.default.settings = {
        user = "alice";
        openssh.authorizedKeys.keys = [ "PASTE_YOUR_KEY_HERE" ];
      };
    };

    # Docs: https://docs.clan.lol/latest/services/official/sshd/
    # SSH service for secure remote access to machines.
    # Generates persistent host keys and configures authorized keys.
    sshd = {
      roles.server.tags.all = { };
      roles.server.settings.authorizedKeys = {
        # Insert the public key that you want to use for SSH access.
        # All keys will have ssh access to all machines ("tags.all" means 'all machines').
        # Alternatively set 'users.users.root.openssh.authorizedKeys.keys' in each machine
        "admin-machine-1" = "PASTE_YOUR_KEY_HERE";
      };
    };

    # Docs: https://docs.clan.lol/latest/services/official/users/
    # Root password management for all machines.
    user-root = {
      module = {
        name = "users";
      };
      roles.default.tags.all = { };
      roles.default.settings = {
        user = "root";
        prompt = true;
      };
    };
  };

  # Additional NixOS configuration can be added here.
  # machines/server/configuration.nix will be automatically imported.
  # See: https://docs.clan.lol/latest/guides/inventory/autoincludes/
  machines = {
    alice-laptop =
      { ... }:
      {
        # Create two folders on alice-laptop
        systemd.tmpfiles.rules = [
          "d /home/alice/documents 0755 alice users -"
          "d /home/alice/pictures 0755 alice users -"
        ];
        clan.core.state."my-documents" = {
          folders = [
            "/home/alice/documents"
            "/home/alice/pictures"
          ];
        };
      };

  };
}
```

Following are notes on the backup-relevant attributes:

**borgbackup:**

This configures the BorgBackup service across two machines with distinct roles:

- Client: `roles.client.machines."alice-laptop"` designates alice-laptop as a backup client — meaning it's a machine whose data will be backed up. The empty {} means no custom client settings; defaults are used.
- Server: `roles.server.machines."backup-server"` designates backup-server as the machine that receives and stores backups from clients. Its settings include:
- address — the IP address where clients should connect to send backups
- directory — the filesystem path on the server where backup repositories are stored

When this config is applied, Clan automatically generates the SSH keys needed for client-to-server authentication, configures the borgbackup service on both machines, and sets up scheduled backup jobs on the client.

**systemd.tmpfiles.rules**

This is a standard NixOS option that uses systemd's tmpfiles mechanism to ensure specific files and directories exist on the system. Each entry is a single string with space-separated fields:

- `d`: the type: create a directory (other types include `f` for file, `L` for symlink, etc.)
- `/home/alice/documents`: the path to create
- `0755`: the permission mode (owner: read/write/execute; group and others: read/execute)
- `alice`: the owning user
- `users`: the owning group
- `-`: the age/cleanup policy; `-` means "don't automatically clean up"

On every boot, systemd checks these rules and creates any missing directories with the specified ownership and permissions. This guarantees the folders exist before any service tries to use them.

**clan.core.state**

This declares a named state entry telling Clan which directories contain important, persistent data that should be preserved across backups.

- "my-documents" is just a label (any name you choose) for this group of stateful folders. It's used internally for tracking and can be referenced in backup hooks.
- folders is the list of filesystem paths Clan should track as state.

When any backup provider (like borgbackup above) runs on this machine, it automatically reads clan.core.state entries and includes their folders in the backup. Each state entry can also define preBackupScript and postBackupScript hooks — useful for services like databases that need to be stopped or flushed before a clean backup can be taken.

## Ready to install

Go through the usual steps (gather hardware configuration for both machines; configure a disk). Then run `clan machines install`, starting with the backup server. The server must be installed first because the client needs the server's SSH host key during setup.

### Set up some files on Alice's computer to back up

Now let's create some documents on Alice's laptop that will be backed up.

Log into alice-laptop as **alice**. If you need her password, on the setup machine, type:

```text
clan vars get alice-laptop user-password-alice/user-password
```

Then log in via SSH:

```text
ssh alice@<IP-ADDRESS>
```

replacing `<IP-ADDRESS>` with the IP address of Alice's laptop virtual machine.

Then, once logged in as **alice**, create some documents, like so:

```bash
cd documents
nano welcome.md
```

Type:

```text
Hello World!
```

Save (Ctrl+O, Enter) and Exit (Ctrl+X)

Now in the same directory create a file called `finance.txt`:

```bash
nano finance.txt
```

Type:

```text
Account total: 5000
```

Save (Ctrl+O, Enter) and Exit (Ctrl+X)

Next, change to the pictures directory:

```bash
cd ~
cd pictures
```

Download any image you like, such as one from the Clan docs:

```text
curl -o hero.jpg https://clan.lol/_assets/25.11/_app/immutable/assets/docs-hero.CUEOsCNu.jpg
```

(We used curl here, because, by default, NixOS ships with curl, but not wget.)

Now check that everything is present:

```text
cd ~
ls documents
ls pictures

```

You should see the two files in `documents` and the `hero.jpg` file in `pictures`.

Exit:

```bash
exit
```

### Perform a backup

Now trigger a backup from the setup machine:

```bash
clan backups create alice-laptop
```

You should see:

```text
successfully started backup
```

Wait a minute or so, and then list the backups:

```bash
clan backups list alice-laptop
```

You'll see a list similar to this:

```text
backup-server::borg@<IP-ADDRESS>:.::alice-laptop-backup-server-2026-04-14T03:53:34
```

Next, log in to alice-laptop and delete a file to simulate data loss:

```text
cd documents
rm welcome.md
```

Exit:

```bash
exit
```

Now back on the setup machine, first list the backups again:

```bash
clan backups list alice-laptop
```

You'll see a list of one item, similar to this:

```text
backup-server::borg@<IP-ADDRESS>:.::alice-laptop-backup-server-2026-04-14T03:53:34
```

If you ran the backup command multiple times, you might see more than one entry. Copy the most recent one to the clipboard, and then type:

```bash
clan backups restore alice-laptop borgbackup <PASTE>
```

For `<PASTE>` paste the backup name from the clipboard, such as:

```bash
clan backups restore alice-laptop borgbackup backup-server::borg@<IP-ADDRESS>:.::alice-laptop-backup-server-2026-04-14T03:53:34
```

Log back in to alice-laptop, return to the `documents` directory, and run `ls`. You should see that `welcome.md` has been restored.

## Backup Commands Reference

For a quick reference, here are the three backup commands used above.

### clan backups create \<machine\>

Triggers an immediate backup of the specified machine across all its configured backup providers.

### clan backups list \<machine\>

Lists all existing backups for the specified machine. Use the optional `--provider` flag to filter by a specific provider.

### clan backups restore \<machine\> \<provider\> \<name\>

Restores a specific backup to the given machine. The <provider> matches the destination name from your configuration, and <name> is one of the backup names returned by clan backups list.
