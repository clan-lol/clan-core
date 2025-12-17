## Summary

It is time: We will finally deploy the machines now!

At this point, the process is the same for VMs and physical hardware.


## Requirements

- Make sure that you prepared your machines according to their type by following the previous steps.

- Double check that each machine has a hardware report saved under ```machines/YOUR-MACHINE-NAME/facter.json```


## Deploying Your Machines

Careful - This command is destructive! It will format your traget device's disk and install NixOS on it!

```shell-session
$ clan machines install [MACHINE] --target-host root@<IP>
```

After the installation completes, your machine will reboot into the newly installed NixOS system.


## Checkpoint

! Work in progress !


## Up Next

In the next step, you will learn how to update your machines after the deployment.
