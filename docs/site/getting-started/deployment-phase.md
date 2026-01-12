## Summary

It is time: We will finally deploy the machines now!

At this point, the process is the same for VMs and physical hardware.


## Requirements

- Make sure that you prepared your machines according to their type by following the previous steps.

- Double check that each machine has a hardware report saved under ```machines/YOUR-MACHINE-NAME/facter.json```

- Double check that each machine has a disk configuration saved under ```machines/YOUR-MACHINE-NAME/disko.nix```

- Make sure your physical targets are booted from the stick as described

- Make sure your virtual targets are in the kexec state as described


## Deploying Your Machines

Careful - This command is destructive! It will format your traget device's disk and install NixOS on it!

```shell-session
$ clan machines install [YOUR-MACHINE-NAME] --target-host root@<IP>
```
Depending on your hardware configurations and network speed, this step may take a few minutes per machine.

You will be asked to set passwords for root and users. You can leave these fields empty, Clan will take care of it.

After the installation completes, your machine will reboot into the newly installed NixOS system and your users will be able to log in.


## Checkpoint

!!! Warning "Under construction"
    We are still working on the best way to confirm a successfull deployment.
    For now, please see if the setup finished by logging in directly on the target machine(s).
    It should ask for `YOUR-MACHINE-NAME login:` and accept an empty password for root (or, if you set a password manually during deployment, that).


## Up Next

In the next step, you will learn how to update your machines after the deployment.
