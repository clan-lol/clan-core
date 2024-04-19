# Installer

We offer a dedicated installer to assist remote installations.

In this tutorial we will guide you through building and flashing it to a bootable USB drive.

## Creating and Using the **Clan Installer**

### Step 0. Prerequisites

- [x] A free USB Drive with at least 1.5GB (All data on it will be lost)
- [x] Linux/NixOS Machine with Internet

### Step 1. Identify the USB Flash Drive

1. Insert your USB flash drive into your computer.

2. Identify your flash drive with `lsblk`:

    ```shellSession
    lsblk
    ```

    ```{.console, .no-copy}
    NAME                                          MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINTS
    sdb                                             8:0    1 117,2G  0 disk
    └─sdb1                                          8:1    1 117,2G  0 part  /run/media/qubasa/INTENSO
    nvme0n1                                       259:0    0   1,8T  0 disk
    ├─nvme0n1p1                                   259:1    0   512M  0 part  /boot
    └─nvme0n1p2                                   259:2    0   1,8T  0 part
      └─luks-f7600028-9d83-4967-84bc-dd2f498bc486 254:0    0   1,8T  0 crypt /nix/store
    ```

    !!! Info "In this case the USB device is `sdb`"

3. Ensure all partitions on the drive are unmounted. Replace `sdb1` in the command below with your device identifier (like `sdc1`, etc.):

```shellSession
sudo umount /dev/sdb1
```

### Step 2. Download the Installer

```shellSession
wget https://github.com/nix-community/nixos-images/releases/download/nixos-unstable/nixos-installer-x86_64-linux.iso
```

### Step 3. Flash the Installer to the USB Drive

!!! Danger "Specifying the wrong device can lead to unrecoverable data loss."

    The `dd` utility will erase the disk. Make sure to specify the correct device (`of=...`)

    For example if the USB device is `sdb` use `of=/dev/sdb`.

    

Use the `dd` utility to write the NixOS installer image to your USB drive:

```shellSession
sudo dd bs=4M conv=fsync oflag=direct status=progress if=./nixos-installer-x86_64-linux.iso of=/dev/sd<X>
```

### Step 4. Boot and Connect to your network

After writing the installer to the USB drive, use it to boot the target machine.

!!! info 
    Plug it into the target machine and select the USB drive as a temporary boot device.

??? tip "Here you can find the key combinations for selection used by most vendors."
    - **Dell**: F12 (Boot Menu), F2/Del (BIOS Setup)
    - **HP**: F9 (Boot Menu), Esc (Startup Menu)
    - **Lenovo**: F12 (ThinkPad Boot Menu), F2/Fn+F2/Novo Button (IdeaPad Boot Menu/BIOS Setup)
    - **Acer**: F12 (Boot Menu), F2/Del (BIOS Setup)
    - **Asus**: F8/Esc (Boot Menu), F2/Del (BIOS Setup)
    - **Toshiba**: F12/F2 (Boot Menu), Esc then F12 (Alternate Method)
    - **Sony**: F11/Assist Button (Boot Menu/Recovery Options)
    - **Samsung**: F2/F12/Esc (Boot Menu), F2 (BIOS Setup)
    - **MSI**: F11 (Boot Menu), Del (BIOS Setup)
    - **Apple**: Option (Alt) Key (Boot Menu for Mac)
    - If your hardware was not listed read the manufacturers instructions how to enter the boot Menu/BIOS Setup.

**During Boot**

Select `NixOS` to boot into the clan installer.

**After Booting**

For deploying your configuration the machine needs to be connected via LAN (recommended).

For connecting via Wifi, please consult the [guide below](#optional-connect-to-wifi).

---

## Whats next?

- [Configure Machines](configure.md): Customize machine configuration
- [Deploying](machines.md): Deploying a Machine configuration
- [WiFi](#optional-connect-to-wifi): Guide for connecting to Wifi.

---

## (Optional) Connect to Wifi

If you don't have access via LAN the Installer offers support for connecting via Wifi.

```shellSession
iwctl
```

This will enter `iwd`

```{.console, .no-copy}
[iwd]#
```

Now run the following command to connect to your Wifi:

```shellSession
# Identify your network device.
device list
# Replace 'wlan0' with your wireless device name
# Find your Wifi SSID.
station wlan0 scan
station wlan0 get-networks

# Replace your_ssid with the Wifi SSID
# Connect to your network.
station wlan0 connect your_ssid

# Verify you are connected
station wlan0 show
```

If the connection was successful you should see something like this:

```{.console, .no-copy}
State                 connected
Connected network     FRITZ!Box (Your router device)
IPv4 address          192.168.188.50 (Your new local ip)
```

Press `ctrl-d` to exit `IWD`.

!!! Important
    Press `ctrl-d` **again** to update the displayed QR code and connection information.

You're all set up
