## NAME 
clan - the clan cli tool

## SYNOPSIS

clan [OPTION...] [SUBCOMMAND]

## DESCRIPTION

**clan** supports managing and deploying various nixos configurations in a unified coherent way. Through the secrets subcommand secrets for machines can be set and retrieved.

For more overview please refer to the reference material at docs.clan.lol.

## OPTIONS

### -h, --help
Output a help message and exit.

### --debug
Enable debug logging.

### --option name value
Nix option to set.

### --flake=FLAKE
Path to the flake where the clan resides in, can be a remote flake, or local.

## SUBCOMMANDS

### clan-backups(1)
Manage backups of clan machines
### clan-flakes(1)
Create a clan flake inside the current directory
### clan-config(1)
Set nixos-configuration
### clan-ssh(1)
SSH to a remote machine
### clan-secrets(1)
Manage secrets
### clan-facts(1)
Manage facts
### clan-machines(1)
Manage machines and their configuration
### clan-vms(1)
Manage virtual machines
### clan-history(1)
Manage history
### clan-flash(1)
Flash machines to usb sticks or into isos
