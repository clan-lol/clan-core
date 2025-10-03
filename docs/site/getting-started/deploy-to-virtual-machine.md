
## Prerequisites
- [x] RAM > 2GB
- [x] **Two Computers**: You need one computer that you're getting ready (we'll call this the Target Computer) and another one to set it up from (we'll call this the Setup Computer). Make sure both can talk to each other over the network using SSH.
- [x] **Machine configuration**: See our basic [adding and configuring machine guide](./add-machines.md)


Clan supports any cloud machine if it is reachable via SSH and supports `kexec`.


??? tip "NixOS can cause strange issues when booting in certain cloud environments."
    If on Linode: Make sure that the system uses "Direct Disk boot kernel" (found in the configuration panel)


The following command will generate a hardware report with [nixos-facter](https://github.com/nix-community/nixos-facter) and writes it back into your machine folder. The `--phases kexec` flag makes sure we are not yet formatting anything, instead if the target system is not a NixOS machine it will use [kexec](https://wiki.archlinux.org/title/Kexec) to switch to a NixOS kernel.


```terminal
clan machines install [MACHINE] \
  --update-hardware-config nixos-facter \
  --phases kexec \
  --target-host myuser@<IP>
```

!!! Warning
    After running the above command, be aware that the SSH login user changes from `myuser` to `root`. For subsequent SSH connections to the target machine, use `root` as the login user. This change occurs because the system switches to the NixOS kernel using `kexec`.
