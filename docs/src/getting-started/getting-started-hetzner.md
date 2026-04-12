# Getting Started: Hetzner Edition

:::admonition[Prerequisites]{type=note}
Your setup machine needs the following:

* **Nix** on your Setup Machine (unless you're using NixOS)

* An **id_ed25519** keypair on your Setup Machine. (Link coming soon.)

* **Git** (Optional). Clan uses Git internally, but you can optionally install it to make your own use of it. See the [Git installation instructions](https://git-scm.com/install/linux).
:::

## 1. Create a Server on Hetzner

:::admonition[Danger]{type=danger}
The steps in this document will erase all data on your Hetzner server's hard drive.
:::

If you already have a server on Hetzner running, you can skip this step.

From the main Hetzner dashboard, in the left pane, click **Servers**.

In the upper right, click **Add Server**.

Choose the type; we recommend either **Regular Performance** or **General Purpose**, because these are newer.

Next, choose the row that best suits your needs; for NixOS you only need the top row, with 2 VCPUs and 2GB or 4GB RAM.

:::admonition[Note]{type=note}
If you change the location, you might see a different set of VCPU and RAM configurations.
:::

For **Image**, choose **Ubuntu**. (This will only be used during installation, after which NixOS will be installed.)

For **Networking**, select at least **Public IPv4**.

Under SSH keys, click **Add SSH key**. Leave this screen open. Open up a command shell on your local machine and type:

```bash
cat ~/.ssh/id_ed25519.pub
```

(If you see "No such file or directory" please visit [this link](/docs/getting-started/create-an-ssh-key) to learn how to create a key pair.)

Paste the contents of the `id_ed25519.pub` file into the **SSH key** box. (We recommend also checking **Set as default key**.) Click **Add SSH key**.

Scroll to the very bottom and under **Name** enter a name of your choice for **Server name** such as `My-Clan-1`.

In the right-hand pane, click **Create && Buy now**.

After a moment the server will be created.

Leave this screen open so you an copy the IP address later by clicking on the IP address.

## 2. Run the Clan setup

Start by creating a new clan:

```text
nix run "https://git.clan.lol/clan/clan-core/archive/main.tar.gz#clan-cli" --refresh -- init
```

and enter a name for it, e.g. `MY-CLAN-1`, followed by a domain, e.g. `myclan1.lol`. (This does not have to be an actual registered domain.)

:::admonition[Important]{type=note}
The first time you run this, Clan will automatically create an age key at `~/.config/sops/age/keys.txt`. This key encrypts your secrets - back it up somewhere safe, and then type "y".
:::

:::admonition[Important]{type=note}
If you've run this before, you'll also be asked to select admin keys; you'll most likely want to type "1" and press enter.
:::

Change to the new folder:

```bash
cd MY-CLAN-1
```

You will see a message about `direnv` needing approval to run. Type:

```bash
direnv allow
```

## 3. Create a Machine Configuration

Next, create a machine configuration, which adds a description of a machine to your inventory. For this example, call it `test-machine`, by typing:

```bash
clan machines create test-machine
```

Open `clan.nix`, and find the `inventory.machines` line; add the following immediately after it; replace the IP address with your Hetzner server's IP address:

```{.nix title="clan.nix" hl_lines="2 3 4 5"}
inventory.machines = { # FIND THIS LINE, ADD THE FOLLOWING
    test-machine = {
        deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS; keep "root@"
        tags = [ ];
    };
```

Test it out:

```bash
clan machines list
```

## 4. Add your allowed keys

Next, add your public key to the allowed keys. You can find it by running:

```bash
cat ~/.ssh/id_ed25519.pub
```

Open `clan.nix`, and replace `PASTE_YOUR_KEY_HERE` with the contents of the `id_ed25519.pub` file:

```text
"admin-machine-1" = "PASTE_YOUR_KEY_HERE";
```

Verify that your configuration is valid:

```bash
clan show
```

## 5. Gather Hardware Configuration

Now gather the hardware configuration from the target machine:

```bash
clan machines init-hardware-config test-machine
```

You will be asked to enter "y" to proceed.

## 6. Add a Disk Configuration.

Next, configure a disk for the target machine. You'll run this command in two steps; first, type it like so:

```bash
clan templates apply disk ext4-single-disk test-machine --set mainDisk ""
```

This will generate an error; note the disk ID it prints out (typically starting with /dev/disk/by-id/scsi-0QEMU_QEMU_HARDDISK_), and add it inside the quotes, e.g.:

```bash
clan templates apply disk ext4-single-disk test-machine --set mainDisk "/dev/disk/by-id/scsi-0QEMU_QEMU_HARDDISK_113572628"
```

## 7. Install NixOS

Install NixOS on the target machine by typing:

```bash
clan machines install test-machine
```

You will be asked whether you want to install — type `y`. You will also be prompted for a password; you can accept the defaults and press Enter.

You will then be asked for a password to assign to the root login for the machine. You can either create one, or let Clan assign a random one.

## If you get an error about Sandboxing

If you get an error regarding sandboxing not being available, type the following to disable sandboxing, and then run the above command again:

```bash
clan vars generate test-machine --no-sandbox
```

## 8. Test the Connection

Now you can try connecting to the remote machine:

```bash
clan ssh test-machine
```

You'll quite likely get an error at first regarding the host identification. It should include a line to type to remove the old ID; paste the line you're shown, which will look similar to this:

```text
  ssh-keygen -f '/home/user/.ssh/known_hosts' -R '<IP-ADDRESS>'
```

Then try again:

```bash
clan ssh test-machine
```

You should connect and see the prompt:

```text
[root@test-machine:~]#
```

## Practice: Install Some Packages

Now let's look at how you can use Clan to install and remove packages on a target machine.

For this demonstration we'll add three command-line packages: `bat`, `btop`, and `tldr`. In clan.nix, under inventory.instances, add the following lines:

```{.nix title="clan.nix" hl_lines="2-6"}
  inventory.instances = {
    packages = {
      roles.default.machines."test-machine".settings = {
        packages = [ "bat" "btop" "tldr" ];
      };
    };
    # ... existing wifi service ...
  };
```

This declares that the three packages will be present on the machine. To install them, type:

```bash
clan machines update test-machine
```

Now ssh into the machine, and they should be present:

```text
which bat
which btop
which tldr
```

Each will show a path to the binary file:

```text
/run/current-system/sw/bin/bat
/run/current-system/sw/bin/btop
/run/current-system/sw/bin/tldr
```

Next, let's remove one of the three packages. The packages portion of clan.nix declares what additional packages should exist; by removing one, Nix will remove that package. Remove the `"tldr"` from the list:

```text
        packages = [ "bat" "btop" ];
```

and run the update again:

```bash
clan machines update test-machine
```

Now when you check which `tldr`, it should show that it's not in the path:

```text
which tldr
which: no tldr in (/run/wrappers/bin:/root/.nix-profile/bin:/nix/profile/bin:/root/.local/state/nix/profile/bin:/etc/profiles/per-user/root/bin:/nix/var/nix/profiles/default/bin:/run/current-system/sw/bin)

```

## Practice: Add a User

When you need to add a new user, you can do so right from within the clan.nix file, and then update the system.

## Add a New User (no sudo access)

Let's add a user called Alice. Open clan.nix, and under inventory.instances, add the following:

```{.nix title="clan.nix" hl_lines="2-9"}
  inventory.instances = { # Add the following under this line
    user-alice = {
      module.name = "users";
      roles.default.machines."test-machine" = {};
      roles.default.tags.all = {};
      roles.default.settings = {
        user = "alice";
      };
    };
```

Save the file. Now type the following to add a password for alice (include the no-sandbox if you needed no sandbox earlier):

```bash
clan vars generate test-machine --no-sandbox
```

You will be prompted for a password. Or you can press Enter to automatically generate one.

If you automatically generated one, to retrieve it type:

```text
clan vars get test-machine user-password-alice/user-password
```

:::admonition[Note]{type=note}
On cloud machines, this password will be used for sudo access if you grant it. Typically password login is disabled on a cloud machine.
:::

Next, let's add a key file so Alice can log in remotely. For this we'll use your own key file as before. Type:

```bash
cat ~/.ssh/id_ed25519.pub
```

Then open `machines/test-machine/configuration.nix`. Add the following, before the closing brace:

```{.nix title="clan.nix" hl_lines="8-10"}
{
  imports = [

  ];

  # New machine!

  users.users.alice.openssh.authorizedKeys.keys = [
    "PASTE_YOUR_KEY_HERE"
  ];
}
```

and replace `PASTE_YOUR_KEY_HERE` with the contents of the file.

Now update the machine by typing:

```bash
clan machines update test-machine
```

Once complete, you can log in as alice:

```bash
ssh alice@<IP-ADDRESS>
```

replacing `<IP-ADDRESS>` with the Hetzner server's IP address.

## Give that user sudo access

After you trust Alice, you can grant her sudo access. To do so, update the clan.nix file by adding her to the wheel group:

```{.nix title="clan.nix" hl_lines="7"}
    user-alice = {
      module.name = "users";
      roles.default.machines."test-machine" = {};
      roles.default.tags.all = {};
      roles.default.settings = {
        user = "alice";
        groups = [ "wheel" ];  # Add this to allow sudo
      };
    };
```

Again type:

```bash
clan machines update test-machine
```

If you were already logged in as alice before running the update, you will need to log out and back in for the change to take.

Then after logged in as alice, try using sudo:

```bash
sudo echo "hello"
```

You will be prompted for the password and should see "hello" printed.

## Revoke the sudo access

To revoke alice's sudo access, simply remove the line you added:

```nix
        groups = [ "wheel" ];

```

And once again run:

```bash
clan machines update test-machine
```

Log out, and log alice back in. Now try the same sudo command; you'll be prompted for password, but then shown:

```text
alice is not in the sudoers file.
```
