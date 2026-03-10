# Introduction to Clan Vars

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
clan vars generate test-machine
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
2. Run: clan vars generate test-machine
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

## Sample Test-Run Walkthrough Without Installing Machines

!!! Tip
    If you want to practice with any of these, you can run the starting nix code to generate a new clan; then you can create a machine configuration without gathering the hardware configuration or writing the machine. You can add the above details to your clan.nix file and try out the commands such as `clan vars generate test-machine` as we demonstrate below.

Let's do a quick test-run walkthrough.

Start with the usual `nix` command:

```bash
nix run "https://git.clan.lol/clan/clan-core/archive/main.tar.gz#clan-cli" --refresh -- init
```

Name it something like `MY-TESTRUN-1` with domain `mytestrun1.lol`.

Next, the usual:

```bash
cd MY-TESTRUN-1
direnv allow
```

Now let's create a laptop configuration for Sally:

```
clan machines create sally-laptop
```

Then add these lines under `inventory.machines` as usual.

```nix
    sally-laptop = {
        deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS; keep "root@"
        tags = [ ];
    };
```

Now let's give Sally her own login on the machine so she doesn't have to use root by adding the following under `inventory.instances`:

```nix
    user-sally = {
      module.name = "users";
      roles.default.machines."sally-laptop" = {};
      roles.default.settings = {
        user = "sally";
      };
    };
```

Now run the vars generate command, but don't enter a password; have clan generate it for you this time by pressing Enter:

```
clan vars generate sally-laptop
```

You will see:

```
Prompting value for user-password-root/user-password for machines: sally-laptop
Leave empty to generate automatically (hidden):
Confirm Leave empty to generate automatically (hidden):
```

(Look closely! This first one is for root.)

Then it asks for Sally's password; this time, provide a password of your choice:

```
Prompting value for user-password-sally/user-password for machines: sally-laptop
Leave empty to generate automatically (hidden):
Confirm Leave empty to generate automatically (hidden):
```

After it finishes, you can retrieve the passwords like so. First, the root password:

```
clan vars get sally-laptop user-password-root/user-password
```

Which displays the random password it generated, such as:

```
dynasty-animate-chemicals-baggie
```

And then Sally's password:

```
clan vars get sally-laptop user-password-sally/user-password
```

And this time you'll see the password you provided, such as:

```
abc123
```

Now let's reset Sally's password for her.

```
clan vars generate sally-laptop --generator user-password-sally --regenerate
```

And you'll see:

```
Prompting value for user-password-sally/user-password for machines: sally-laptop
Leave empty to generate automatically (hidden):
Confirm Leave empty to generate automatically (hidden):
```

!!! Note "Important"
    If you do this after deployment, you'll have to push this password to the machine using `clan machines update sally-laptop`.

Finally, let's do a few things at once: Let's add another machine called `fred-laptop`, and let's add wireless configuration to both machines.

First, create the machine configuration:

```bash
clan machines create fred-laptop
```

Then, add the following under `inventory.machines`:

```nix
    fred-laptop = {
        deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS; keep "root@"
        tags = [ ];
    };
```

Now add the following inside `inventory.instances` under the user-sally attribute set:

```
    user-fred = {
      module.name = "users";
      roles.default.machines."fred-laptop" = {};
      roles.default.settings = {
        user = "fred";
      };
    };
```

Now we're going to create some tags. Tags are just labels we assign to machines, and then we can access all those machines from that single tag. Let's assign the tag "laptop" to both `sally-laptop` and `fred-laptop`. Uppdate the two attribute sets inside `inventory.machine = {` by adding the string "laptop" to the tags:

```{.nix title="clan.nix" hl_lines="3, 7"}
    sally-laptop = {
        deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS; keep "root@"
        tags = [ "laptop" ];
    };
    fred-laptop = {
        deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS; keep "root@"
        tags = [ "laptop" ];
    };
    # Define machines here.
    # server = { };
  };

```

And then inside `inventory.instances` (probably under the user-fred attribute set), add the following:

```nix
    wifi = {
      roles.default.tags.laptop = {
        settings.networks.home = { };
      };
    };
```

(We've pasted the entire clan.nix at the end of this section for your reference.)

Look carefully at the above; we're assigning the same network to the machines that have the `laptop` tag.

Now generate; we do each machine separately, but watch how it only asks for the WiFi name and password once:

```bash
clan vars generate sally-laptop
```

You'll see the following:

```
Prompting value for wifi.home/network-name for machines: fred-laptop, sally-laptop
name of the Wi-Fi network: MYNETWORK
Input received. Processing...
Prompting value for wifi.home/password for machines: fred-laptop, sally-laptop
Enter the value for wifi.home/password: (hidden):
Confirm Enter the value for wifi.home/password: (hidden):
```

Notice how the fourth line is prompting for the wifi password for both machines, even though the command was run only for Sally's machine. This is good, since they should match.

Now generate for Fred:

```bash
clan vars generate fred-laptop
```

(Be careful! Sometimes the order changes and it asks for Fred's password before root.)

```
Prompting value for user-password-fred/user-password for machines: fred-laptop
Leave empty to generate automatically (hidden):
Confirm Leave empty to generate automatically (hidden):
Input received and confirmed. Processing...
Prompting value for user-password-root/user-password for machines: fred-laptop
Leave empty to generate automatically (hidden):
Confirm Leave empty to generate automatically (hidden):
```

And notice it did not ask for the WiFi name and password, since it was already set earlier.

!!! Note
    Even though the above was a test run walkthrough, you can still continue with gathering machine configurations, creating a disk, and installing if you want. Indeed, the above represent the preparation steps for a clan.

Here's the entire clan.nix file:

```nix
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "MY-TESTRUN-1";
  meta.domain = "mytestrun1.lol";

  inventory.machines = {
    sally-laptop = {
        deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS; keep "root@"
        tags = [ "laptop" ];
    };
    fred-laptop = {
        deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS; keep "root@"
        tags = [ "laptop" ];
    };
    # Define machines here.
    # server = { };
  };

  # Docs: See https://docs.clan.lol/latest/services/definition/
  inventory.instances = {

    user-sally = {
      module.name = "users";
      roles.default.machines."sally-laptop" = {};
      roles.default.settings = {
        user = "sally";
      };
    };

    user-fred = {
      module.name = "users";
      roles.default.machines."fred-laptop" = {};
      roles.default.settings = {
        user = "fred";
      };
    };

    wifi = {
      roles.default.tags.laptop = {};
      roles.default.settings.networks.home = {};
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
        "admin-machine-1" = "__YOUR_PUBLIC_KEY__";
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

    # Docs: https://docs.clan.lol/latest/services/official/zerotier/
    # The lines below will define a zerotier network and add all machines as 'peer' to it.
    # !!! Manual steps required:
    #   - Define a controller machine for the zerotier network.
    #   - Deploy the controller machine first to initialize the network.
    zerotier = {
      # Replace with the name (string) of your machine that you will use as zerotier-controller
      # See: https://docs.zerotier.com/controller/
      # Deploy this machine first to create the network secrets
      roles.controller.machines."__YOUR_CONTROLLER__" = { };
      # Peers of the network
      # tags.all means 'all machines' will joined
      roles.peer.tags.all = { };
    };

    # Docs: https://docs.clan.lol/latest/services/official/tor/
    # Tor network provides secure, anonymous connections to your machines
    # All machines will be accessible via Tor as a fallback connection method
    tor = {
      roles.server.tags.nixos = { };
    };
  };

  # Additional NixOS configuration can be added here.
  # machines/server/configuration.nix will be automatically imported.
  # See: https://docs.clan.lol/latest/guides/inventory/autoincludes/
  machines = {
    # server = { config, ... }: {
    #   environment.systemPackages = [ pkgs.asciinema ];
    # };
  };
}
```