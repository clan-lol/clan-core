# More on Backups

## Backup Hooks: Pre/Post Scripts

Sometimes you need to stop a service before backing up its data (to avoid corrupted files), then start it again after. Clan supports this with hooks.

Hooks are defined as part of state, not as part of the backup service, because stopping a service before a backup is really about the *data*, not the backup tool.

For example, you might be backing up a machine running Docker containers. You generally don't want to back up container volumes while the containers are actively writing to them, as the backup could capture inconsistent state.

The following partial example shows how to pause all Docker containers before the backup and resume them afterward:

```nix
  machines = {

    docker-host = { config, ... }: {
      clan.core.state."containers" = {
        folders = [ "/var/lib/docker/volumes" ];
        preBackupScript = ''
          docker pause $(docker ps -q)
        '';
        postBackupScript = ''
          docker unpause $(docker ps -q)
        '';
      };
    };

  };

```

Other cases where pre/post backup hooks are useful:

- Databases (see the complete PostgreSQL example below)
- Virtual machines (stop the VM to get a consistent disk image)
- Mail servers (pause delivery during backup)
- Monitoring tools with append-only data files (e.g., Prometheus, InfluxDB)
- Log rotation (rotate logs before backup for a clean cutoff)

In general, use hooks for any service with live, mutable state.

There are four hooks available:

| Hook | When It Runs |
|------|-------------|
| `preBackupScript` | Before the backup starts |
| `postBackupScript` | After the backup finishes |
| `preRestoreScript` | Before a restore starts |
| `postRestoreScript` | After a restore finishes |

## PostgreSQL Database Backups

Clan has built-in support for PostgreSQL. Instead of manually writing pre/post scripts to dump and restore databases, you can use the `clan.core.postgresql` module, which integrates automatically with the backup system.

Below is a complete clan.nix example:

```nix
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "MY-HETZNER-CLAN";
  meta.domain = "myhetznerclan.lol";

  inventory.machines = {
    postgres-server = {
      deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH POSTGRES-SERVER'S IP ADDRESS; keep "root@"
      tags = [ ];
    };
    backup-server = {
      deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH BACKUP-SERVER'S IP ADDRESS; keep "root@"
      tags = [ ];
    };
  };

  # Docs: See https://docs.clan.lol/latest/services/definition/
  inventory.instances = {

    borgbackup = {
      roles.client.machines."postgres-server" = { };
      roles.server.machines."backup-server" = {
        settings.address = "<IP-ADDRESS>"; # REPLACE WITH BACKUP-SERVER'S IP ADDRESS
        settings.directory = "/var/lib/borgbackup";
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
        "admin-machine-1" = "[PASTE_YOUR_KEY_HERE]";
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

    postgres-server =
      { config, ... }:
      {
        services.postgresql = {
          enable = true;
          ensureDatabases = [ "mydatabase" ];
        };

        clan.core.postgresql.enable = true;
        clan.core.postgresql.databases.mydatabase = { };

        clan.core.state."postgresql" = {
          folders = [ ];
          preBackupScript = ''
            systemctl stop postgresql
          '';
          postBackupScript = ''
            systemctl start postgresql
          '';
        };
      };

  };
}
```

## Backing up two machines

The following clan.nix file demonstrates how to back up two machines, a laptop (`alice-laptop`) and a database server (`postgres-server`), to a single backup server (`backup-server`).

Note that `alice-laptop` has a tag called `"employees"`. The borgbackup service uses this tag to automatically include any machine tagged `"employees"` as a client, so adding the tag to a new machine is all that's needed to back it up.

### Installation Order

When setting up borgbackup (or any service with cross-machine dependencies), the order in which you install your machines matters.

The borgbackup client needs the server's SSH host key to establish a connection. This key is generated during the server's installation. If you install a client machine before the server, the client won't be able to find the server's key, and you'll need to re-generate its vars afterward. To avoid this, install the backup server before any client machines:

```bash
clan machines install backup-server --target-host root@<BACKUP-IP>
```

```bash
clan machines install postgres-server --target-host root@<POSTGRES-IP>
```

```bash
clan machines install alice-laptop --target-host root@<ALICE-IP>
```

This applies to any service where one machine depends on another machine's generated secrets — always install or generate vars for the machine that provides the secret before the machines that consume it.

```nix
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "MY-BACKUP-CLAN";
  meta.domain = "mybackupclan.lol";

  inventory.machines = {
    alice-laptop = {
      deploy.targetHost = "root@192.168.56.101";
      tags = [ "employees" ];
    };
    backup-server = {
      deploy.targetHost = "root@192.168.56.104";
      tags = [ ];
    };
    postgres-server = {
      deploy.targetHost = "root@192.168.56.102";
      tags = [ ];
    };
  };

  inventory.instances = {
    borgbackup = {
      roles.client.tags = [ "employees" ];
      roles.client.machines."postgres-server" = { };
      roles.server.machines."backup-server" = {
        settings.address = "192.168.56.104";
        settings.directory = "/var/lib/borgbackup";
      };
    };

    user-alice = {
      module.name = "users";
      roles.default.machines."alice-laptop" = { };
      roles.default.settings = {
        user = "alice";
        openssh.authorizedKeys.keys = [
          "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAZGMNlooljzJfmzQKaVcmj4tRYW+gqBIfdWbG0NU3XL freckleface@freckleface--Laptop"
        ];
      };
    };

    sshd = {
      roles.server.tags.all = { };
      roles.server.settings.authorizedKeys = {
        "admin-machine-1" =
          "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAZGMNlooljzJfmzQKaVcmj4tRYW+gqBIfdWbG0NU3XL freckleface@freckleface--Laptop";
      };
    };

    user-root = {
      module.name = "users";
      roles.default.tags.all = { };
      roles.default.settings = {
        user = "root";
        prompt = true;
      };
    };
  };

  machines = {

    alice-laptop =
      { ... }:
      {
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

    postgres-server =
      { config, ... }:
      {
        services.postgresql = {
          enable = true;
          ensureDatabases = [ "mydb" ];
        };

        clan.core.postgresql.enable = true;
        clan.core.postgresql.databases.mydb = { };

        clan.core.state."postgresql" = {
          folders = [ ];
          preBackupScript = ''
            systemctl stop postgresql
          '';
          postBackupScript = ''
            systemctl start postgresql
          '';
        };
      };

  };
}
```

## Excluding files and folders

You can exclude files and folders from the backup using this general pattern:

```nix
roles.client.tags.employees.settings = {
  exclude = [ "*.bak" ]; 
}
```

This would exclude all files ending with .bak on every machine tagged with employees.

Here's an example that excludes multiple patterns on a specific machine:

```nix
inventory.instances = {
  borgbackup = {
    roles.client.machines."alice-laptop" = {
      settings.exclude = [
        "*.pyc"
        "*.tmp"
        "__pycache__"
        ".cache"
      ];
    };
    roles.server.machines."backup-server" = {};
  };
};
```

## Changing the Backup Schedule

The default schedule is 1:00 AM daily. To change it, add `startAt` to the client settings:

```nix
inventory.instances = {
  borgbackup = {
    roles.client.machines."alice-laptop" = {
      settings.startAt = "*-*-* 04:00:00";   # 4 AM daily
    };
    roles.server.machines."backup-server" = {};
  };
};
```

The schedule uses [systemd calendar event syntax](https://www.freedesktop.org/software/systemd/man/systemd.time.html).

Here are some examples of the pattern:

| Schedule | Meaning |
|----------|---------|
| `*-*-* 01:00:00` | Every day at 1 AM (default) |
| `*-*-* 04:00:00` | Every day at 4 AM |
| `*-*-* *:00:00` | Every hour |
| `Mon *-*-* 03:00:00` | Every Monday at 3 AM |

Below is a partial clan.nix file that demonstrates three workstations backing up to a NAS, each on a different schedule:

```nix
# clan.nix
{
  inventory.machines = {
    laptop = {
      deploy.targetHost = "root@192.168.1.10";
      tags = [ "workstation" ];
    };
    desktop = {
      deploy.targetHost = "root@192.168.1.11";
      tags = [ "workstation" ];
    };
    work-pc = {
      deploy.targetHost = "root@192.168.1.12";
      tags = [ "workstation" ];
    };
    nas = {
      deploy.targetHost = "root@192.168.1.50";
    };
  };

  inventory.instances = {
    borgbackup = {
      roles.client.machines = {
        "laptop" = {
          settings.startAt = "*-*-* 02:00:00";
        }; # 2 AM
        "desktop" = {
          settings.startAt = "*-*-* 03:00:00";
        }; # 3 AM
        "work-pc" = {
          settings.startAt = "*-*-* 04:00:00";
        }; # 4 AM
      };
      roles.server.machines."nas" = {
        settings.address = "192.168.1.50";
        settings.directory = "/data/backups";
      };
    };
  };
}
```

## External Backup Destinations

You don't have to back up to another Clan machine. You can add external destinations like a Hetzner Storage Box or any SSH-accessible BorgBackup server.

Create a storage box on Hetzner (or use an existing one). If creating it, make sure to check **Allow SSH** and **External Reachability** under **Additional Settings**. Also, follow the on-screen instructions to add your own `id_ed25519.pub` key.

Create a new clan, replace the entire `clan.nix` file with the one below, and fill in the clan name and domain you chose. Then create the `postgres-server` machine, gather its hardware configuration, and configure a disk as usual.

```nix
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "MY-HETZNER-CLAN";
  meta.domain = "myhetznerclan.lol";

  inventory.machines = {
    postgres-server = {
      deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH postgres-server's IP ADDRESS; keep "root@"
      tags = [ ];
    };
  };

  inventory.instances = {

    borgbackup = {
      roles.client.machines."postgres-server" = {
        settings.destinations."storagebox" = {
          repo = "<BOX-USERID>@<BOX-USERID>.your-storagebox.de:/./borgbackup"; # REPLACE WITH USERNAME FROM STORAGE BOX DETAILS PAGE
          rsh = "ssh -p 23 -oStrictHostKeyChecking=accept-new -i /run/secrets/vars/borgbackup/borgbackup.ssh";
        };
      };
    };

    sshd = {
      roles.server.tags.all = { };
      roles.server.settings.authorizedKeys = {
        # Insert the public key that you want to use for SSH access.
        # All keys will have ssh access to all machines ("tags.all" means 'all machines').
        # Alternatively set 'users.users.root.openssh.authorizedKeys.keys' in each machine
        "admin-machine-1" = "PASTE_YOUR_KEY_HERE";
      };
    };

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

  machines = {

    postgres-server =
      { config, ... }:
      {
        services.postgresql = {
          enable = true;
          ensureDatabases = [ "mydatabase" ];
        };

        clan.core.postgresql.enable = true;
        clan.core.postgresql.databases.mydatabase = { };

        clan.core.state."postgresql" = {
          folders = [ ];
          preBackupScript = ''
            systemctl stop postgresql
          '';
          postBackupScript = ''
            systemctl start postgresql
          '';
        };
      };

  };
}
```

In the Hetzner web console, go to the storage box overview and copy the username and server URL into the `clan.nix` file where indicated.

Now run `clan machines install` to install postgres-server. During installation, Clan generates an SSH keypair for borgbackup. After installation, retrieve the public key and upload it to your storage box. The first command below simply prints the key (use it for any SSH-accessible server other than Hetzner); the second is for Hetzner; pipes it directly to a Hetzner storage box. Replace `<BOX-USERID>` with your storage box username.

```bash
# For non-Hetzner: Get the public key Clan generated
clan vars get postgres-server borgbackup/borgbackup.ssh.pub

# For Hetzner Storage Box, you can pipe it directly:
clan vars get postgres-server borgbackup/borgbackup.ssh.pub | ssh -p23 <BOX-USERID>@<BOX-USERID>.your-storagebox.de install-ssh-key
```

Here's a breakdown of the `rsh` attribute:

```nix
rsh = "ssh -p 23 -oStrictHostKeyChecking=accept-new -i /run/secrets/vars/borgbackup/borgbackup.ssh";
```

- **`rsh`**: stands for "remote shell." This borgbackup setting defines the command used to connect to the remote repository.
- **`ssh`**: use SSH for the connection.
- **`-p 23`**: connect on port 23 (Hetzner's SSH port for storage boxes, instead of the default port 22).
- **`-oStrictHostKeyChecking=accept-new`** — controls host key verification:
    - `yes` (default) would require the host key to already be in `known_hosts`, otherwise refuse
    - `no` would blindly accept anything (insecure)
    - `accept-new` is the sweet spot — accepts new hosts on first connection automatically, but rejects if the key changes later (protecting against man-in-the-middle attacks)
- **`-i /run/secrets/vars/borgbackup/borgbackup.ssh`**: the Clan-generated borgbackup private key, deployed to postgres-server under `/run/secrets/` (a RAM-only directory, so the key never touches disk). This is the private half of the public key you uploaded to Hetzner.

In plain English: "Connect via SSH on port 23, auto-trust new hosts but reject changed ones, and authenticate with the borgbackup private key from secrets."

## Configuring multiple backups for a single client

A single client can back up to multiple destinations simultaneously. The following clan.nix file backs `postgres-server` to both a local VM and a Hetzner storage box:

```nix
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "MY-BACKUP-CLAN";
  meta.domain = "mybackupclan.lol";

  inventory.machines = {
    postgres-server = {
      deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH POSTGRES-SERVER'S IP ADDRESS; keep "root@"
      tags = [ ];
    };
    backup-server = {
      deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH BACKUP-SERVER'S IP ADDRESS; keep "root@"
      tags = [ ];
    };
  };

  # Docs: See https://docs.clan.lol/latest/services/definition/
  inventory.instances = {

    borgbackup = {
      roles.client.machines."postgres-server" = {
        # declares postgres-server a client (ONE time)
        settings.destinations."storagebox" = {
          # Destination #1
          repo = "<HETZNER-USER>@<HETZNER-USER>.your-storagebox.de:/./borgbackup"; # REPLACE <HETZNER-USER> with your Hetzner storage box username
          rsh = "ssh -p 23 -oStrictHostKeyChecking=accept-new -i /run/secrets/vars/borgbackup/borgbackup.ssh";
        };
      };
      roles.server.machines."backup-server" = {
        # default server
        settings.address = "<IP-ADDRESS>"; # REPLACE WITH BACKUP-SERVER'S IP ADDRESS
        settings.directory = "/var/lib/borgbackup";
      };
    };

    # Docs: https://docs.clan.lol/latest/services/official/sshd/
    # SSH service for secure remote access to machines.
    sshd = {
      roles.server.tags.all = { };
      roles.server.settings.authorizedKeys = {
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
  machines = {

    postgres-server =
      { config, ... }:
      {
        services.postgresql = {
          enable = true;
          ensureDatabases = [ "mydatabase" ];
        };

        clan.core.postgresql.enable = true;
        clan.core.postgresql.databases.mydatabase = { };

        clan.core.state."postgresql" = {
          folders = [ ];
          preBackupScript = ''
            systemctl stop postgresql
          '';
          postBackupScript = ''
            systemctl start postgresql
          '';
        };
      };

  };
}
```

A client machine backs up to every server in the borgbackup instance for which it's a client, plus any explicit destinations listed under its own settings.destinations.

Under the hood, Clan generates one systemd `borgbackup-job-*` unit per destination. So `postgres-server` gets two scheduled jobs:

- borgbackup-job-backup-server (to the local VM)

- borgbackup-job-storagebox (to Hetzner)

Both run on the same schedule and both honor the pre/post backup hooks, meaning postgres gets cleanly stopped/started around each backup independently.
