# Getting Started: VirtualBox Edition

## 🚧 Draft — Under Active Development (but ready for brief review)

!!! Note Prerequisites
    Your setup machine needs the following:

* **VirtualBox**: The virtualization software. Download it from the [official site](https://www.virtualbox.org/wiki/Downloads).

* **Nix** on your Setup Machine (unless you're using NixOS)

* An **id_ed25519** keypair on your Setup Machine. [Click here](./id_ed25519.md) to find it or, if necessary, create it.

* **Git** (Optional). Clan uses Git internally, but you can optionally install it to make your own use of it. You can find installation instructions [here](https://git-scm.com/install/linux).


# 1. Download the Installer ISO Image

Type the following to download the installer's ISO image:

```bash
wget https://github.com/nix-community/nixos-images/releases/download/nixos-unstable/nixos-installer-x86_64-linux.iso
```

# 2. Install the ISO and run it

## Setup the VirtualBox Machine

In VirtualBox, click **New**.

Provide a name for the **Name** box, such as NixOS Installer.

Leave Folder the default.

Click the dropdown to the right of ISO Image. Choose **Other**. Navigate to the location of your download. Choose `nixos-installer-x86_64-linux.iso`. Click **Open**.

For **Type**, select **Linux**.

For Version, scroll near the top, and select **Linux 2.6 / 3.x / 4.x / 5.x (64-bit)**.

Click **Next**. Now you'll choose the amount of memory and CPU cores. If you have enough memory and CPU installed, you'll want to type **8192** into the box to the right of **Base Memory**, and at least **3** to the right of **Processors**. Keep **Enable EFI (special OSes only)** *unchecked*. Click Next.

For Virtual Hard Disk, choose **Create a Virtual Hard Disk Now**, and in the box to the right, type **20**. (Remember, this is just practice, and we don't expect you'll want to keep this installation going after you create it. So 20GB should be plenty.)

Click **Next**.

Click **Finish**.

*Do not run the machine yet!* We still have another item to configure. Right click on your new **NixOS Installer** machine, and choose **Settings**. In the left side, choose **Network**. Under the **Adapter 1** tab, click the **Attached to** dropdown, and choose **Bridged Adapter**. Leave **Name** as is. Click **OK**.


NOTE: Windows VirtualBox is different!

OS Edition: Leave blank
OS: Linux
OS Distribution: Other Linux
OS Version: Other Linux (64-bit)



## Run the VirtualBox Machine

Make sure **NixOS Installer** is selected (it will have a blue background). 

In the upper right, click **Start**.

You will see the NixOS loader start; simply wait. You'll see text scroll and finally a screen will open that starts with a QR code, followed by:

* Login Crednetials. Below this is the root password for logging into the installer. (Not the installed NixOS after the procedure is complete.)

* Network Information. Take note of the IP address, such as 10.0.0.18.

* Remote Access. The host name has been added to your DNS; instead of 10.0.0.18 you can use this name, but that name will go away after NixOS is installed. Instead use make note of IP address.

# 3. Run the Clan setup

nix run "https://git.clan.lol/clan/clan-core/archive/main.tar.gz#clan-cli" --refresh -- init

cd MY...
direnv allow...

# 4. Create a Machine Configuration

clan machines create test-machine

```{.nix title="clan.nix" hl_lines="2 3 4 5"}
inventory.machines = { # FIND THIS LINE, ADD THE FOLLOWING
    test-machine = {
        deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS; keep "root@"
        tags = [ ];
    };
```

Add the IP address shown in the screen with the QR code

cat ~/.ssh/id_ed25519.pub

PASTE_YOUR_KEY_HERE

# 5. Gather Hardware Configuration

Now it's time to gather info on your hardware. Type:

```
clan machines init-hardware-config test-machine --target-host root@<IP-ADDRESS>
```

replacing <IP-ADDRESS> with the IP address shown beneith the QR code.

You will be asked to enter "y" to proceed.

When prompted for password, use the password displayed under the QR code.

# 6. Add a Disk Configuration.

Next, configure a disk for the target machine. You'll run this command in two steps; first, type it like so:

```
clan templates apply disk single-disk test-machine --set mainDisk ""
```

This will generate an error; note the disk ID it prints out (typically starting with /dev/disk/by-id/ata-VBOX_HARDDISK_VB), and add it inside the quotes, e.g.:

```
clan templates apply disk single-disk test-machine --set mainDisk "/dev/disk/by-id/ata-VBOX_HARDDISK_VB..."
```

# 7. Install NixOS

Install NixOS on the target machine by typing:

clan machines install test-machine --target-host root@<IP-ADDRESS>

Again substituting IP-ADDRESS as before.

(You will be asked whether you want to install; type y. You will also be asked about a password; you can accept the defaults here and just press Enter for both.)

You will then be asked for a password to assign to the root login for the machine. You can either create one, or let Clan assign a random one.

### If you get an error about Sandboxing

If you get an error regarding sandboxing not being available, type the following to disable sandboxing, and then run the above command again:

```bash
clan vars generate test-machine --no-sandbox
```

# 8. Test Connection

Now you can try connecting to the remote machine:

```bash
clan ssh test-machine
```

You'll quite likely get an error at first regarding the host identification. It should include a line to type to remove the old ID; paste the line you're shown, which will look similar to this:
```
  ssh-keygen -f '/home/user/.ssh/known_hosts' -R '<IP-ADDRESS>'
```

Then try again:

```bash
clan ssh test-machine
```

You should connect and see the prompt:

```
[root@test-machine:~]#
```

# Practice: Install Some Packages

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

```
which bat
which btop
which tldr
```

Each will show a path to the binary file:

```
/run/current-system/sw/bin/bat
/run/current-system/sw/bin/btop
/run/current-system/sw/bin/tldr
```

Next, let's remove one of the three packages. The packages portion of clan.nix declares what additional packages should exist; by removing one, Nix will remove that package. Remove the `"tldr"` from the list:
```
        packages = [ "bat" "btop" ];
```

and run the update again:

```bash
clan machines update my-machine
```

Now when you check which `tldr`, it should show that it's not in the path:

```
which tldr
which: no tldr in (/run/wrappers/bin:/root/.nix-profile/bin:/nix/profile/bin:/root/.local/state/nix/profile/bin:/etc/profiles/per-user/root/bin:/nix/var/nix/profiles/default/bin:/run/current-system/sw/bin)

```

# Practice: Add a User

When you need to add a new user, you can do so right from within the clan.nix file, and then update the system.





