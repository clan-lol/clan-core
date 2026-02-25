## Adding Additional Machines

## 🚧 Early Notes Draft — Not Ready for Review, but okay to glance at for technical mistakes

When you're ready to add additional machines, remember that you will add them to your existing clan.

!!! Note Important
    You do not run the original nix command again; that creates a new clan, which is not what you want here.


!!! Tip
    If you're creating virtual machines with VirtualBox, repeat the steps for creating a new virtual machine; we recommend naming it the same as what you use below, such as test2-machine. Then start it up and note its IP address and password.

Once you've followed the steps in either Getting Started Guide for your initial machine, you will then make sure you're in the directory containing your clan, and repeat the steps but with a new machine name, starting with:

```bash
clan machines create test2-machine
```

Here we're creating a machine called test2-machine.

Next, open `clan.nix` and add a second machine name in inventory.machines; if you already had test-machine, then add test2-machine below it, along with its new IP address:

```nix
inventory.machines = { # FIND THIS LINE, ADD THE FOLLOWING
    test-machine = {
        deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH YOUR FIRST MACHINE'S IP ADDRESS; keep "root@"
        tags = [ ];
    };
    test2-machine = {
        deploy.targetHost = "root@<IP-ADDRESS>"; # REPLACE WITH YOUR SECOND MACHINE'S IP ADDRESS; keep "root@"
        tags = [ ];
    };
```

Exit the editor, and test it out:

```bash
clan machines list
```

!!! Tip
    You do not need to add an additional entry for the authorized key.

Then the three remaining steps as before; make sure to use test2-machine:

### Gather Hardware Configuration

```bash
clan machines init-hardware-config test2-machine --target-host root@<IP-ADDRESS>
```

clan templates apply disk single-disk test2-machine --set mainDisk ""

which will generate an error; copy the name listed to the clipboard, and then type:

```bash
clan templates apply disk single-disk test2-machine --set mainDisk "/dev/disk/by-id/ata-VBOX_HARDDISK_VB..."
```

### Install NixOS

Finally, you can run the installer:

```bash
clan machines install test2-machine --target-host root@<IP-ADDRESS>
```

### Test out the connection

Now you should be able to connect via ssh:

```bash
clan ssh test2-machine
```