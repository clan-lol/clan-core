## Summary

In this step, we will prepare your virtual machines to be deployed from your setup machine and integrated into your Clan automatically.


## Requirements
* **Setup Device**: The same setup device you were using during the previous steps.
* **Target Device(s)**: Any number of virtual Linux or macOS devices with SSH root access to.

    !!! Warning "Operating System Recommendations"
        We are currently working on more refined operating system recommendations.

        - Minimum system requirements: 2 CPUs, 4GB RAM, 30gb HDD space, network interface

        - We currently recommend NixOS 25.11 for this guide, but other Linux systems are supported, too.

        - Root user access will be required throughout the whole setup.

* **Machine configuration**: In the previous steps, we defined a Clan, at least one user (e.g. jon) and at least one machine (e.g. jon-machine). These are the minimum requirements for the following VM preparations.

* **Network Root Access**: Target and setup machine need to be able to reach each other, root access is required on both, and ssh access needs to be available on the targets (configured already if you followed all optional steps up to this point).

* **kexec**: Clan supports any cloud machine if it supports `kexec`.


??? tip "NixOS can cause strange issues when booting in certain cloud environments."
    If on Linode: Make sure that the system uses "Direct Disk boot kernel" (found in the configuration panel)


## Generating Hardware Reports

A hardware report needs to  be created on each target machine before the actual deployment.

The following command will generate the hardware report with [nixos-facter](https://github.com/nix-community/nixos-facter) and write it back into the respective machine folder on your setup device. 

The command will use [kexec](https://wiki.archlinux.org/title/Kexec) to boot the target into a minimal NixOS environment to gather the hardware information.


```terminal
clan machines init-hardware-config [YOUR-MACHINE-NAME] \
  --target-host myuser@<IP>
```

!!! Warning
    After running the above command, be aware that the SSH login user changes from `myuser` to `root`. For subsequent SSH connections to the target machine, use `root` as the login user. This change occurs because the system switches to the NixOS kernel using `kexec`.


## Checkpoint: Confirming the Hardware Reports

For each machine, check if the hardware report was saved under 
```machines/YOUR-MACHINE-NAME/facter.json```
 on your setup device.


## Up Next

After the report is generated for all target machines, we will configure the disk layout in the next step and then deploy the machines remotely.
