## Setting up Encryption with Remote Decryption in NixOS

This guide provides an example setup for a single-disk ZFS system with native encryption, accessible for decryption remotely. This configuration only applies to `systemd-boot` enabled systems and requires UEFI booting.

For a mirrored disk setup, add `mode = "mirror";` to `zroot`. Under the `disk` option, provide the additional disk identifier, e.g., `y = mirrorBoot /dev/disk/by-id/<second_disk_id>`.

Replace the disk `nvme-eui.002538b931b59865` with your own. 

Below is the configuration for `disko.nix`
```nix
{ lib, ... }:
let
  mirrorBoot = idx: {
    type = "disk";
    device = "/dev/disk/by-id/${idx}";
    content = {
      type = "gpt";
      partitions = {
        boot = {
          size = "1M";
          type = "EF02"; # for grub MBR
          priority = 1;
        };
        ESP = lib.mkIf (idx == "nvme-eui.002538b931b59865") {
          size = "1G";
          type = "EF00";
          content = {
            type = "filesystem";
            format = "vfat";
            mountpoint = "/boot";
            mountOptions = [ "nofail" ];
          };
        };
        zfs = {
          size = "100%";
          content = {
            type = "zfs";
            pool = "zroot";
          };
        };
      };
    };
  };
in
{
  boot.loader.systemd-boot.enable = true;

  disko.devices = {
    disk = {
      x = mirrorBoot "nvme-eui.002538b931b59865";
    };
    zpool = {
      zroot = {
        type = "zpool";
        rootFsOptions = {
          compression = "lz4";
          acltype = "posixacl";
          xattr = "sa";
          "com.sun:auto-snapshot" = "true";
          mountpoint = "none";
        };
        datasets = {
          "root" = {
            type = "zfs_fs";
            options = {
              mountpoint = "none";
              encryption = "aes-256-gcm";
              keyformat = "passphrase";
              keylocation = "file:///tmp/secret.key";
            };
          };
          "root/nixos" = {
            type = "zfs_fs";
            options.mountpoint = "/";
            mountpoint = "/";
          };
          "root/home" = {
            type = "zfs_fs";
            options.mountpoint = "/home";
            mountpoint = "/home";
          };
          "root/tmp" = {
            type = "zfs_fs";
            mountpoint = "/tmp";
            options = {
              mountpoint = "/tmp";
              sync = "disabled";
            };
          };
        };
      };
    };
  };
}
```

Add this to networking.nix and **replace** the `default` values as well as the name `gchq-local` and `networking.hostId` with your own.

```nix
{ config, lib, ... }:
{
  options = {
    networking.gchq-local.ipv4.address = lib.mkOption {
      type = lib.types.str;
      default = "192.168.178.177";
    };
    networking.gchq-local.ipv4.cidr = lib.mkOption {
      type = lib.types.str;
      default = "24";
    };

    networking.gchq-local.ipv4.gateway = lib.mkOption {
      type = lib.types.str;
      default = "192.168.178.1";
    };

    networking.gchq-local.ipv6.address = lib.mkOption {
      type = lib.types.str;
      default = "2003:100:6701:d500:fbbc:40fb:cff3:3b87";
    };

    networking.gchq-local.ipv6.cidr = lib.mkOption {
      type = lib.types.str;
      default = "64";
    };
    networking.gchq-local.ipv6.gateway = lib.mkOption {
      type = lib.types.str;
      default = "fe80::3ea6:2fff:feef:3435";
    };
  };

  config = {
    networking.dhcpcd.enable = false;
    networking.nameservers = [ "127.0.0.1" ];
    networking.hostId = "a76ebcca"; # Needs to be unique for each host

    # The '10' in the network name is the priority, so this will be the first network to be configured
    systemd.network.networks."10-eth" = {
      matchConfig.Type = "ether";
      addresses = [
        {
          Address=config.networking.gchq-local.ipv4.address + "/" + config.networking.gchq-local.ipv4.cidr;
        }
        {
          Address=config.networking.gchq-local.ipv6.address + "/" + config.networking.gchq-local.ipv6.cidr;
        }
      ];
      DHCP = "yes";
    };
  };
}
```

Put this into initrd.nix and add your pubkey to `authorizedKeys`.
Replace `kernelModules` with the ethernet module loaded one on your system.
```nix
{config, pkgs, ...}:

{

  boot.initrd.systemd = {
    enable = true;
    network.networks."10-eth" = config.systemd.network.networks."10-eth";
  };
  boot.initrd.network = {
    enable = true;

    ssh = {
      enable = true;
      port = 7172;
      authorizedKeys = [ "<yourkey>" ];
      hostKeys = [
        "/var/lib/initrd-ssh-key"
      ];
    };
  };
  boot.initrd.availableKernelModules = [
    "xhci_pci"
  ];

  # Check the network card by running `lspci -k` on the target machine
  boot.initrd.kernelModules = [ "r8169" ];
}
```


### Step 1: Copying SSH Public Key

Before starting the installation process, ensure that the SSH public key is copied to the NixOS installer.

1. Copy your public SSH key to the installer, if it has not been copied already:

```bash
ssh-copy-id -o PreferredAuthentications=password -o PubkeyAuthentication=no root@nixos-installer.local
```

### Step 1.5: Prepare Secret Key and Clear Disk Data

1. Access the installer using SSH:

```bash
ssh root@nixos-installer.local
```

2. Create a `secret.key` file in `/tmp` using `nano` or another text editor:

```bash
nano /tmp/secret.key
```

3. Discard the old disk partition data:

```bash
blkdiscard /dev/disk/by-id/nvme-eui.002538b931b59865
```

4. Run the `clan` machine installation with the following command:

```bash
clan machines install gchq-local root@nixos-installer --yes --no-reboot
```

### Step 2: ZFS Pool Import and System Installation

1. SSH into the installer once again:

```bash
ssh root@nixos-installer.local
```

2. Perform the following commands on the remote installation environment:

```bash
zpool import zroot
zfs set keystate=prompt zroot/root
zfs load-key zroot/root
zfs set mountpoint=/mnt zroot/root/nixos
mount /dev/nvme0n1p2 /mnt/boot
```

3. Disconnect from the SSH session:

```bash
CTRL+D
```

4. Securely copy your local `initrd_rsa_key` to the installer's `/mnt` directory:

```bash
scp ~/.ssh/initrd_rsa_key root@nixos-installer.local:/mnt/var/lib/initrd-ssh-key
```

5. SSH back into the installer:

```bash
ssh root@nixos-installer.local
```

6. Navigate to the `/mnt` directory, enter the `nixos-enter` environment, and then exit:

```bash
cd /mnt
nixos-enter
realpath /run/current-system
exit
```

7. Run the `nixos-install` command with the appropriate system path `<SYS_PATH>`:

```bash
nixos-install --no-root-passwd --no-channel-copy --root /mnt --system <SYS_PATH>
```

8. After the installation process, unmount `/mnt/boot`, change the ZFS mountpoint, and reboot the system:

```bash
umount /mnt/boot
cd /
zfs set mountpoint=/ zroot/root/nixos
reboot
```

9. Perform a hard reboot of the machine and remove the USB stick.

### Step 3: Accessing the Initial Ramdisk (initrd) Environment

1. SSH into the initrd environment using the `initrd_rsa_key` and provided port:

```bash
ssh -p 7172 root@192.168.178.141
```

2. Run the `systemd-tty-ask-password-agent` utility to query a password:

```bash
systemd-tty-ask-password-agent --query
```

After completing these steps, your NixOS should be successfully installed and ready for use.

**Note:** Replace `root@nixos-installer.local` and `192.168.178.141` with the appropriate user and IP addresses for your setup. Also, adjust `<SYS_PATH>` to reflect the correct system path for your environment.