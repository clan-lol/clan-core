
# Update Your Machines

Clan CLI enables you to remotely update your machines over SSH. This requires setting up a target address for each target machine.

### Setting `targetHost`

In your nix files set the targetHost (reachable ip) that your new machine now has. This removes the need to add `--targetHost` to every command.


```{.nix title="clan.nix" hl_lines="9"}
{
# Ensure this is unique among all clans you want to use.
meta.name = "my-clan";

inventory.machines = {
    # Define machines here.
    # The machine name will be used as the hostname.
    jon = {
        deploy.targetHost = "root@192.168.192.4"; # (1)
    };
};
# [...]
}
```
The use of `root@` in the target address implies SSH access as the `root` user.
Ensure that the root login is secured and only used when necessary.


### Setting a Build Host

If the machine does not have enough resources to run the NixOS evaluation or build itself,
it is also possible to specify a build host instead.
During an update, the cli will ssh into the build host and run `nixos-rebuild` from there.


```{.nix hl_lines="5" .no-copy}
buildClan {
    # ...
    machines = {
        "jon" = {
            clan.core.networking.buildHost = "root@<host_or_ip>";
        };
    };
};
```

!!! Note
    Make sure that the CPU architecture is the same for the buildHost as for the targetHost.
    Example:
        If you want to deploy to a macOS machine, your architecture is an ARM64-Darwin, that means you need a second macOS machine to build it.

### Updating Machine Configurations

Execute the following command to update the specified machine:

```bash
clan machines update jon
```

You can also update all configured machines simultaneously by omitting the machine name:

```bash
clan machines update
```


### Excluding a machine from `clan machine update`

To exclude machines from being updated when running `clan machines update` without any machines specified,
one can set the `clan.deployment.requireExplicitUpdate` option to true:

```{.nix hl_lines="5" .no-copy}
buildClan {
    # ...
    machines = {
        "jon" = {
            clan.deployment.requireExplicitUpdate = true;
        };
    };
};
```

This is useful for machines that are not always online or are not part of the regular update cycle.
