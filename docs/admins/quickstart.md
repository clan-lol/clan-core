# Getting Started with Your First Clan Project

Welcome to your simple guide on starting a new Clan project!

## What's Inside

We've put together a straightforward guide to help you out:

- [**Starting with a New Clan Project**](#starting-with-a-new-clan-project): Create a new Clan from scratch.
- [**Migrating Existing Flake Configuration**](migrate.md#migrating-existing-nixos-configuration-flake): How to switch your current setup to a Clan setup.
- [**Integrating Clan using Flake-Parts**](./migrate.md#integrating-clan-with-flakes-using-flake-parts)

---

## Starting with a New Clan Project

Create your own clan with these initial steps:

### Step 1: Add Clan CLI to Your Shell

Add the Clan CLI into your development workflow:

```shell
nix shell git+https://git.clan.lol/clan/clan-core
```

### Step 2: Initialize Your Project

Set the foundation of your Clan project by initializing it as follows

```shell
clan flakes create my-clan
```

This command creates the `flake.nix` and `.clan-flake` files for your project.

### Step 3: Verify the Project Structure

Ensure the creation of your project files with a quick directory listing

```shell
cd my-clan && ls -la
```

You should see `.clan-flake`, `flake.lock`, and `flake.nix` among the files listed, which means you're all set up!

---

### Next Steps

### Edit Flake.nix

Open the `flake.nix` file and set a unique `clanName` if you want you can also set an optional `clanIcon` or even a per `machineIcon`. These will be used by our future clan GUI.

### Remote into the target machine

**Right now clan assumes that you already have NixOS running on the target machine.**

If that is not the case you can use our [installer image](./install-iso.md) that automatically generates an endpoint reachable over TOR with a random ssh password.

On the remote execute:
1. Generate a hardware-config.nix 
    ```bash
    nixos-generate-config --root /etc/nixos --no-filesystems
    ```
2. Copy it over and put it into you `machines/jon/hardware-config.nix` folder
    ```bash
    scp -r root@<jon-ip>:/etc/nixos/hardware-config.nix ./machines/jon
    ```
3. Find the remote disk id by executing on the remote:
    ```bash
    lsblk --output NAME,ID-LINK,FSTYPE,SIZE,MOUNTPOINT
    ```
4. Edit the following fields inside the `flake.nix`
    - `clan.networking.targetHost = pkgs.lib.mkDefault "root@<IP_ADDRESS>";`
    - `clan.diskLayouts.singleDiskExt4 = {
                  device = "/dev/disk/by-id/__CHANGE_ME__";
                };`

5. Generate secrets used by clan modules by executing
    ```bash
    clan facts generate
    ```

### **Next Steps**
Ready to expand? Explore how to install a new machine with the helpful documentation [here](./machines.md).
Ready to explore more?

- **Adding New Machines to your setup**. [Following our template](/templates/new-clan/flake.nix)

- **Use a USB drive to Set Up Machines**: Setting up new computers remotely is easy with a USB stick. [Learn how] (./machines.md).

---
