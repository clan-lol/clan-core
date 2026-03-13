# Getting Started: Physical Machine Target

:::admonition[Tip]{type=tip}
Prefer to use a Virtual Machine as a target? [Find the guide here](/docs/getting-started/getting-started-virtualbox).
:::

:::admonition[Prerequisites]{type=note}
Your setup machine needs the following:
:::

* **Nix** on your Setup Machine (unless you're using NixOS)

* An **SSH key** on your setup machine. See [Create an SSH key](/docs/getting-started/create-an-ssh-key) if you don't have one yet.

* **Git** (Optional). Clan uses Git internally, but you can optionally install it to make your own use of it. You can find installation instructions [here](https://git-scm.com/install/linux).

## Terminology

**Setup machine** This is the computer you'll be working from to set up and manage your other machines.

**Target machine** This is one (or more) computers that you'll be managing. These can be either physical or virtual machines.

**Machine configuration** Clan's own internal representation of a target machine.

## 1. Create the clan

Start by creating a new clan:

```
nix run "https://git.clan.lol/clan/clan-core/archive/main.tar.gz#clan-cli" --refresh -- init
```

and enter a name for it, e.g. `MY-CLAN-1`, followed by a domain, e.g. `myclan1.lol`. (This does not have to be an actual registered domain.)

:::admonition[Important]{type=note}
The first time you run this, Clan will automatically create an age key at ~/.config/sops/age/keys.txt. This key encrypts your secrets - back it up somewhere safe, and then type "y".
:::

:::admonition[Important]{type=note}
If you've run this before, you'll also be asked to select admin keys; you'll most likely want to type "1" and press enter.
:::

Change to the new folder:

```bash
cd MY-CLAN-1
```

You will see a message about `direnv` needing approval to run. Type:

```
direnv allow
```

## 2. Create a machine configuration

Next create a machine configuration, which adds a description of a machine to your inventory. For this example, call it `test-machine`, by typing:

```
clan machines create test-machine
```

Open `clan.nix`, and find the `inventory.machines` line; add the following immediately after it. (You will add the IP address later in this guide.)

```nix [clan.nix] {2,3,4,5}
inventory.machines = { # FIND THIS LINE, ADD THE FOLLOWING
    test-machine = {
        deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS; keep "root@"
        tags = [ ];
    };
```

Test it out:
```
clan machines list
```

## 3. Add your allowed keys

Next, add your public key to the allowed keys. You can find it by running:

```bash
cat ~/.ssh/id_ed25519.pub
```

Open `clan.nix`, and replace `PASTE_YOUR_KEY_HERE` with the contents of the `id_ed25519.pub` file:

```
"admin-machine-1" = "PASTE_YOUR_KEY_HERE";
```

Verify that your configuration is valid:

```bash
clan show
```

## 4. Enable WiFi on Target Machine (Optional)

If you plan to manage your physical machine through WiFi, you will need to add the following to your `clan.nix` file under `inventory.instances`:

```nix [clan.nix] {2-6}
  inventory.instances = {
    wifi = {
      roles.default.machines."test-machine" = {
        settings.networks.home = { };
      };
    };
```

This will allow WiFi to be used on the target machine *after* installation.

## 5. Create an Installer USB Drive

Obtain a USB drive with at least 1.5 GB total space.

:::admonition[Danger]{type=note}
All data on the USB drive will be lost!
:::

First, download the installer ISO image for your target machine's architecture:

For x86_64 machines:

```bash
wget https://github.com/nix-community/nixos-images/releases/download/nixos-25.11/nixos-installer-x86_64-linux.iso
```

For aarch64 (ARM) machines:

```bash
wget https://github.com/nix-community/nixos-images/releases/download/nixos-25.11/nixos-installer-aarch64-linux.iso
```

Insert the USB drive into your setup computer. Determine its block device name by typing:

```bash
lsblk
```

You will see output similar to this; look under the `SIZE` column to find the entry that matches the USB drive's size. (It will likely be sda or sdb):

```console {2}
NAME                                          MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINTS
sdb                                             8:0    1 117,2G  0 disk
└─sdb1                                          8:1    1 117,2G  0 part  /run/media/qubasa/INTENSO
nvme0n1                                       259:0    0   1,8T  0 disk
├─nvme0n1p1                                   259:1    0   512M  0 part  /boot
└─nvme0n1p2                                   259:2    0   1,8T  0 part
    └─luks-f7600028-9d83-4967-84bc-dd2f498bc486 254:0    0   1,8T  0 crypt /nix/store
```

Unmount the device; replace `sdb` below with your own identifier, and repeat for each mounted partition, for example:

```bash
sudo umount /dev/sdb1
sudo umount /dev/sdb2
sudo umount /dev/sdb3
```

Now flash the ISO to the USB drive using `dd`. Replace `<USB_DEVICE>` with your device name (e.g. `sdb`) and `<ISO_FILE>` with the downloaded filename:

```bash
sudo dd if=<ISO_FILE> of=/dev/<USB_DEVICE> bs=4M status=progress conv=fsync
```

For example:

```bash
sudo dd if=nixos-installer-x86_64-linux.iso of=/dev/sdb bs=4M status=progress conv=fsync
```

## 6. Plug in and Run the Installer

You now have an installer USB that you can remove and plug into the target computer and boot to the USB drive.

:::admonition[Tip]{type=tip}
You might need to disable secure boot. Follow our instructions [here](https://docs.clan.lol/25.11/guides/secure-boot/).
:::

Once booted, you will see a QR code and text similar to this:

```
│ ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│ │Local network addresses:                                                         │ │
│ │enp1s0           UP    192.168.000.001/24 metric 1024 fe80::21e:6ff:fe45:3c92/64 │ │
│ │enp2s0           DOWN                                                            │ │
│ │wlan0            DOWN # connect to wlan (3)                                      │ │
│ │Onion address: 6evxy5yhzytwpnhc2vpscrbti3iktxdhpnf6yim6bbs25p4v6beemzyd.onion    │ │
│ │Multicast DNS: nixos-installer.local                                             │ │
│ └─────────────────────────────────────────────────────────────────────────────────┘ │
│ Press 'Ctrl-C' for console access
```

Take note of the IP address displayed above, either for wireless or lan, depending on how you connected. Then return to the setup machine and update this line that you added to the `clan.nix` file earlier; add in the actual IP address:

```
deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS;
```

:::admonition[Important]{type=note}
If you find there's no IP address listed (and instead it shows "DOWN" then proceed to the next section to enable wireless).
:::

## 7. Enabling Wireless *During* Installation

To enable wireless during installation, press Ctrl+C to drop to a command-line prompt, and type:

```bash
nmtui
```

In the GUI that opens:

1. Press Down-Arrow to get to `Activate a Connection` and press `Enter`.
2. In the list that appears, arrow-down to the same network your setup computer is connected to.
3. Press the Right Arrow to highlight the "\<Activate\>" button.
4. Enter the password when asked, or push the button on the router.
5. Press Esc, then arrow-down to `Quit`.

You should now be online. You can test it by:

```bash
ping www.clan.lol
```

Press **Ctrl+D** to return to the installer app, and note the IP address, and add it to the `clan.nix` file as described earlier.


## 8. Get Hardware Configuration

Now gather the hardware configuration from the target machine:

```
clan machines init-hardware-config test-machine --target-host root@<IP-ADDRESS>
```

Replace `<IP-ADDRESS>` with the IP address of your target machine.

You will be asked to enter "y" to proceed.


## 9. Add a disk configuration

Next, configure a disk for the target machine. You'll run this command in two steps; first, type it like so:

```
clan templates apply disk single-disk test-machine --set mainDisk ""
```

This will generate an error; note the disk ID it prints out (typically starting with /dev/disk/by-id), and add it inside the quotes, e.g.:

```
clan templates apply disk single-disk test-machine --set mainDisk "/dev/disk/by-id/..."
```

## 10. Install

Install NixOS on the target machine by typing:

```
clan machines install test-machine --target-host root@<IP-ADDRESS>
```

Replace `<IP-ADDRESS>` with the target machine's IP address as before.

You will be asked whether you want to install — type `y`. You will also be prompted for WiFi credentials (use the same network your setup machine is on) and a root password (you can either create one or let Clan assign a random one).

### If you get an error about Sandboxing

If you get an error regarding sandboxing not being available, type the following to disable sandboxing, and then run the above command again:

```bash
clan vars generate test-machine --no-sandbox
```

You may need to re-enter the WiFi credentials and root password. Then run the install again:

```bash
clan machines install test-machine --target-host <USER>@<IP-ADDRESS>
```

After completion, remove the USB drive before the machine reboots. You may need to reboot manually.

## 11. Test Connection

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


Now let's look at how you can use Clan to install and remove packages on a target machine.

For this demonstration we'll add three command-line packages: `bat`, `btop`, and `tldr`. In clan.nix, under inventory.instances, add the following lines:

```nix [clan.nix] {2-6}
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
clan machines update test-machine
```

Now when you check which `tldr`, it should show that it's not in the path:

```
which tldr
which: no tldr in (/run/wrappers/bin:/root/.nix-profile/bin:/nix/profile/bin:/root/.local/state/nix/profile/bin:/etc/profiles/per-user/root/bin:/nix/var/nix/profiles/default/bin:/run/current-system/sw/bin)

```


When you need to add a new user, you can do so right from within the clan.nix file, and then update the system.

## Add a New User (no sudo access)

Let's add a user called Alice. Open clan.nix, and under inventory.instances, add the following:

```nix [clan.nix] {2-9}
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

```
clan vars get test-machine user-password-alice/user-password
```

Now update the machine by typing:

```bash
clan machines update test-machine
```

Once complete, you can log in as alice with the password on the target machine.

## Give that user sudo access

After you trust Alice, you can grant her sudo access. To do so, update the clan.nix file by adding her to the wheel group:


```nix [clan.nix] {7}
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

Then after logged in, try using sudo:

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

```
alice is not in the sudoers file.
```
