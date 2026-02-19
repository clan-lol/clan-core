# Getting Started: Physical Machine Target

!!! Note Prerequisites
    Your setup machine needs the following:

* **Nix** on your Setup Machine (unless you're using NixOS)

* An **id_ed25519** keypair on your Setup Machine. [Click here](./id_ed25519.md) to find it or, if necessary, create it.

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

!!! Note Important
    The first time you run this, Clan will automatically create an age key at ~/.config/sops/age/keys.txt. This key encrypts your secrets - back it up somewhere safe, and then type "y".

!!! Note Important
    If you've run this before, you'll also be asked to select admin keys; you'll most likely want to type "1" and press enter.

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

```{.nix title="clan.nix" hl_lines="2 3 4 5"}
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

Next you will add your key to the allowedKeys. Your best bet to finding it is:

```bash
cat ~/.ssh/id_ed25519.pub
```

Open `clan.nix`, and replace `PASTE_YOUR_KEY_HERE` with the contents of the `id_ed25519.pub` file:

```
"admin-machine-1" = "PASTE_YOUR_KEY_HERE"; 
```

Test out your .nix file to make sure it's not broken:

```bash
clan show
```

## 4. To Enable WiFi on Target Machine (if no Lan)

If you plan to manage your physical machine through WiFi, you will need to add the following to your `clan.nix` file under `inventory.instances`:

```{.nix title="clan.nix" hl_lines="2-6"}
  inventory.instances = {
    wifi = {
      roles.default.machines."test-machine" = {
        settings.networks.home = { };
      };
    };
```

This will allow WiFi to be used on the target machine *after* installation.

## 5. Create an Installer USB Drive

Obtain a USB drive with at least 1.5  GB total space.

!!! Note Danger
    All data on the USB drive will be lost!

Insert it into your setup computer. Determine its block name by typing:

```bash
lsblk
```

You will see output similar to this; look under `SIZE` column to find the entry that matches the USB drive's size. (It will likely be sda or sdb):

```{.shellSession hl_lines="2" .no-copy}
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

Now type the following, replacing <USB_DEVICE> with your own identifier, without the number, e.g. `sdb`:

```bash
clan flash write --flake https://git.clan.lol/clan/clan-core/archive/main.tar.gz \
  --ssh-pubkey $HOME/.ssh/id_ed25519.pub \
  --keymap us \
  --language en_US.UTF-8 \
  --disk main /dev/<USB_DEVICE> \
  flash-installer
```

## 6. Plug in and Run the Installer

You now have an installer USB that you can remove and plug into the target computer and boot to the USB drive.

!!! Tip
    You might need to disable secure boot. Follow our instructions [here](https://docs.clan.lol/25.11/guides/secure-boot/).

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

!!! Note Important
    If you find there's no IP address listed (and instead it shows "DOWN" then proceed to the next section to enable wireless).

## 7. Enabling Wireless *During* Installation

To enable wireless during installation, press Ctrl+C to drop to a command-line prompt, and type:

```bash
nmtui
```

In the GUI that opens:

1. Press Down-Arrow to get to `Activate a Connection`.
2. In the list that appears, arrow-down to the same network your setup computer is connected to.
3. Press the Right Arrow to highlight the "<Activate>" button.
4. Enter the password when asked, or push the button on the router.
5. Press Esc, then arrow-down to `Quit`.

You should now be online. You can test it by:

```bash
ping www.clan.lol
```

Press **Ctrl+D** to return to the installer app, and note the IP address, and add it to the `clan.nix` file as described earlier.


## 8. Get Hardware Configuration

Now it's time to gather info on your hardware. Type:

```
clan machines init-hardware-config test-machine --target-host root@<IP-ADDRESS>
```

replacing <IP-ADDRESS> with the IP address of your system

You will be asked to enter "y" to proceed.


## 9. Prepare a disk

Next, configure a disk for the target machine. You'll run this command in two steps; first, type it like so:

```
clan templates apply disk single-disk test-machine --set mainDisk ""
```

This will generate an error; note the disk ID it prints out, and add it inside the quotes, e.g.:

```
clan templates apply disk single-disk test-machine --set mainDisk "/dev/xvda"
```

## 10. Install

Install NixOS on the target machine by typing:

```
clan machines install test-machine --target-host <USER>@<IP-ADDRESS>
```

Again substituting USERNAME and IP-ADDRESS as before.

(You will be asked whether you want to install; type y. You will also be asked about a password; you can accept the defaults here and just press Enter for both.)

You will also be asked for the WiFi username and password for the machine to be configured with. Make sure it's the same network your setup machine is on.

You will then be asked for a password to assign to the root login for the machine. You can either create one, or let Clan assign a random one.

### If you get an error about Sandboxing

If you get an error regarding sandboxing not being available, type the following to disable sandboxing, and then run the above command again:

```bash
clan vars generate test-machine --no-sandbox
```

And for WiFi, you might need to repeat that network name and password.

You will also have to enter a new root password again here, or let Clan assign one. Then run the installer again:

```bash
clan machines install test-machine --target-host <USER>@<IP-ADDRESS>
```

After completion, for physical machines, remove the USB drive, before the machine reboots. (You may need to reboot manually.)

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

# Practice: Install Packages

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
clan machines update my-machine
```

Now ssh into the machine, and they should be present:

```bash
which bat
which btop
which tldr
```

should each show a path to the binary file.

Next, let's remove one of the three packages. The packages portion of clan.nix declares what additional packages should exist; by removing one, Nix will remove that package. Remove the `"tldr"` from the list:
```
        packages = [ "bat" "btop" ];
```

and run the update again:

```bash
clan machines update my-machine
```

Now when you check which tldr, it should show that it's not in the path:

```
which tldr
```
