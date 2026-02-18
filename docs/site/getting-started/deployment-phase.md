## Summary

Deploy machines to their target devices. The process is the same for VMs and physical hardware.


## Requirements

- Make sure that you prepared your machines according to their type by following the previous steps.

- Double check that each machine has a hardware report saved under `machines/$MACHINE_NAME/facter.json`

- Double check that each machine has a disk configuration saved under `machines/$MACHINE_NAME/disko.nix`

- Make sure your physical targets are booted from the stick as described

- Make sure your virtual targets are in the kexec state as described


## Deploying Your Machines

Careful - This command is destructive! It will format your target device's disk and install NixOS on it!

```bash
clan machines install $MACHINE_NAME --target-host root@$TARGET_IP
```
Depending on your hardware configurations and network speed, this step may take a few minutes per machine.

You will be asked to set passwords for root and users. You can leave these fields empty, Clan will take care of it.

After the installation completes, your device will reboot into the newly installed NixOS system and your users will be able to log in.


## Checkpoint

To verify the deployment succeeded:

1. The target machine should reboot automatically after installation
2. You should see a login prompt displaying `$MACHINE_NAME login:`
3. Log in as `root` with the password you set during deployment (or empty if you skipped the prompt)
4. Run `clan machines update $MACHINE_NAME` from your workstation — it should complete without errors


## Up Next

In the next step, you will learn how to update your machines after the deployment.
