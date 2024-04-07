# Managing NixOS Machines with Clan

Clan CLI, in conjunction with [nixos-anywhere](https://github.com/nix-community/nixos-anywhere), provides a seamless method for installing NixOS on various machines.
This process involves preparing a suitable hardware and disk partitioning configuration and ensuring the target machine is accessible via SSH.

### Prerequisites

- [x] A running Linux system with SSH on the target machine is required. This is typically pre-configured for many server providers.

### Finishing the installation

With the target machine running Linux and accessible via SSH, execute the following command to install NixOS on the target machine, replacing `<target_host>` with the machine's hostname or IP address:

```bash
clan machines install my-machine <target_host>
```

## Update Your Machines

Clan CLI enables you to remotely update your machines over SSH. This requires setting up a target address for each target machine.

### Setting the Target Host

Replace `host_or_ip` with the actual hostname or IP address of your target machine:

```bash
clan config --machine my-machine clan.networking.targetHost root@host_or_ip
```

> Note: The use of `root@` in the target address implies SSH access as the `root` user.
> Ensure that the root login is secured and only used when necessary.

### Updating Machine Configurations

Execute the following command to update the specified machine:

```bash
clan machines update my-machine
```

You can also update all configured machines simultaneously by omitting the machine name:

```bash
clan machines update
```

### Setting a Build Host

If the machine does not have enough resources to run the NixOS evaluation or build itself,
it is also possible to specify a build host instead.
During an update, the cli will ssh into the build host and run `nixos-rebuild` from there.

```bash
clan config --machine my-machine clan.networking.buildHost root@host_or_ip
```

### Excluding a machine from `clan machine update`

To exclude machines from beeing updated when running `clan machines update` without any machines specified,
one can set the `clan.deployment.requireExplicitUpdate` option to true:

```bash
clan config --machine my-machine clan.deployment.requireExplicitUpdate true
```

This is useful for machines that are not always online or are not part of the regular update cycle.

---

# TODO:
* TODO: How to join others people zerotier
  * `services.zerotier.joinNetworks = [ "network-id" ]`
* Controller needs to approve over webinterface or cli