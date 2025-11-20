By default clan uses [disko](https://github.com/nix-community/disko) which allows for declarative disk partitioning.

To see what disk templates are available run:
```{.shellSession hl_lines="11" .no-copy}
$ clan templates list

Available 'clan' templates
├── <builtin>
│   ├── default: Initialize a new clan flake
│   ├── flake-parts: Flake-parts
│   ├── flake-parts-minimal: Minimal flake-parts clan template
│   └── minimal: for clans managed via (G)UI
Available 'disko' templates
├── <builtin>
│   └── single-disk: A simple ext4 disk with a single partition
Available 'machine' templates
├── <builtin>
│   ├── flash-installer: Initialize a new flash-installer machine
│   └── new-machine: Initialize a new machine
```


For this guide we will select the `single-disk` template, that uses `A simple ext4 disk with a single partition`.

!!! tip
    For advanced partitioning, see [Disko templates](https://github.com/nix-community/disko-templates) or [Disko examples](https://github.com/nix-community/disko/tree/master/example).
    You can also [contribute a disk template to clan core](https://docs.clan.lol/guides/disko-templates/community/)


To setup a disk schema for a machine run

```bash
clan templates apply disk single-disk jon --set mainDisk ""
```

Which should fail and give the valid options for the specific hardware:

```shellSession
Invalid value  for placeholder mainDisk - Valid options:
/dev/disk/by-id/nvme-WD_PC_SN740_SDDQNQD-512G-1201_232557804368
```

Re-run the command with the correct disk:

```bash
clan templates apply disk single-disk jon --set mainDisk "/dev/disk/by-id/nvme-WD_PC_SN740_SDDQNQD-512G-1201_232557804368"
```

Should now be successful

```shellSession
Applied disk template 'single-disk' to machine 'jon'
```

A disko.nix file should be created in `machines/jon`
You can have a look and customize it if needed.

!!! Danger
    Don't change the `disko.nix` after the machine is installed for the first time, unless you really know what you are doing.
    Changing disko configuration requires wiping and reinstalling the machine.

## Deploy the machine

**Finally deployment time!**

This command is destructive and will format your disk and install NixOS on it! It is equivalent to appending `--phases kexec,disko,install,reboot`.


```bash
clan machines install [MACHINE] --target-host root@<IP>
```


