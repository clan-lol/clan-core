# Flash

Flashes your machine to an USB drive

Usage: `clan flash`

!!! info "Commands"
    - **[list](#flash-list)**: 
    - **[write](#flash-write)**: 
    

### Examples
`  $ clan flash write mymachine --disk main /dev/sd<X> --ssh-pubkey ~/.ssh/id_rsa.pub`

  Will flash the machine 'mymachine' to the disk '/dev/sd<X>' with the ssh public key '~/.ssh/id_rsa.pub'.

For more detailed information, visit: [getting-started](../../getting-started/prepare-physical-machines.md)
            


## Flash list

Usage: `clan flash list`

!!! info "Positional arguments"
    1. **cmd**: list possible languages or keymaps
    
??? info "Options"
    - **--debug**: Enable debug logging
    - **--option**: `<('name', 'value')>` Nix option to set
    - **--flake**: `<PATH>` path to the flake where the clan resides in, can be a remote flake or local, can be set through the [CLAN_DIR] environment variable
    
## Flash write

Usage: `clan flash write`

!!! info "Positional arguments"
    1. **machine**: machine to install
    
??? info "Options"
    - **--disk**: `<('name', 'device')>` The device where flash to.
                    name: The name of the 'device' in the disk configuration. Example: 'main' <- disko.devices.disk.main.
                    device: The name of the physical 'device' where the utility will be flashed to. Example: '/dev/sda/'
    - **--mode**: (Default: `format`) Specify the mode of operation. Valid modes are: format, mount."
        Format will format the disk before installing.
        Mount will mount the disk before installing.
        Mount is useful for updating an existing system without losing data.
    - **--ssh-pubkey**: ssh pubkey file to add to the root user. Can be used multiple times
    - **--language**: system language
    - **--keymap**: system keymap
    - **--yes**: do not ask for confirmation
    - **--dry-run**: Only build the system, don't flash it
    - **--write-efi-boot-entries**: Write EFI boot entries to the NVRAM of the system for the installed system.
        Specify this option if you plan to boot from this disk on the current machine,
        but not if you plan to move the disk to another machine.
    - **--debug**: Enable debug logging
    - **--option**: `<('name', 'value')>` Nix option to set
    - **--flake**: `<PATH>` path to the flake where the clan resides in, can be a remote flake or local, can be set through the [CLAN_DIR] environment variable
    
