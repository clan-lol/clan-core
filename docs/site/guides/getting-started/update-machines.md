# Update Machines

The Clan command line interface enables you to update machines remotely over SSH.
In this guide we will teach you how to set a `targetHost` in Nix,
and how to define a remote builder for your machine closures.


## Setting `targetHost`

Set the machine’s `targetHost` to the reachable IP address of the new machine.
This eliminates the need to specify `--target-host` in CLI commands.

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

## Multiple Target Hosts

You can now experiment with a new interface that allows you to define multiple `targetHost` addresses for different VPNs. Learn more and try it out in our [networking guide](../networking/networking.md).

## Updating Machine Configurations

Execute the following command to update the specified machine:

```bash
clan machines update jon
```

All machines can be updated simultaneously by omitting the machine name:

```bash
clan machines update
```

---

## Advanced Usage

The following options are only needed for special cases, such as limited resources, mixed environments, or private flakes.

### Setting `buildHost`

If the machine does not have enough resources to run the NixOS **evaluation** or **build** itself,
it is also possible to specify a `buildHost` instead.
During an update, clan will ssh into the `buildHost` and run `nixos-rebuild` from there.

!!! Note
    The `buildHost` option should be set directly within your machine’s Nix configuration, **not** under `inventory.machines`.


```{.nix hl_lines="5" .no-copy}
clan {
    # ...
    machines = {
        "jon" = {
            clan.core.networking.buildHost = "root@<host_or_ip>";
        };
    };
};
```

### Overriding configuration with CLI flags

`buildHost` / `targetHost`, and other network settings can be temporarily overridden for a single command:

For the full list of flags refer to the [Clan CLI](../../reference/cli/index.md)

```bash
# Build on a remote host
clan machines update jon --build-host root@192.168.1.10

# Build locally (useful for testing or when the target has limited resources)
clan machines update jon --build-host local
```

!!! Note
    Make sure the CPU architecture of the `buildHost` matches that of the `targetHost`

    For example, if deploying to a macOS machine with an ARM64-Darwin architecture, you need a second macOS machine with the same architecture to build it.


### Excluding a machine from `clan machine update`

To exclude machines from being updated when running `clan machines update` without any machines specified,
one can set the `clan.deployment.requireExplicitUpdate` option to true:

```{.nix hl_lines="5" .no-copy}
clan {
    # ...
    machines = {
        "jon" = {
            clan.deployment.requireExplicitUpdate = true;
        };
    };
};
```

This is useful for machines that are not always online or are not part of the regular update cycle.

### Uploading Flake Inputs

When updating remote machines, flake inputs are usually fetched by the build host.
However, if flake inputs require authentication (e.g., private repositories),

Use the `--upload-inputs` flag to upload all inputs from your local machine:

```bash
clan machines update jon --upload-inputs
```

This is particularly useful when:
- The flake references private Git repositories
- Authentication credentials are only available on local machine
- The build host doesn't have access to certain network resources
