### Summary

Congratulations! You have successfully created your first Clan.

You configured machines, users, and services and are able to manage your Clan through machine updates.

Here are a few ideas to pursue next:


### Generate Vars

Typically, this step is handled automatically when a machine is deployed. However, to enable the use of `nix flake check` with your configuration, it must be completed manually beforehand.

To generate all necessary variables and secrets, execute the following command:

```sh
clan vars generate
```


### Check Configuration

Validate your configuration by running:

```bash
nix flake check
```

This command helps ensure that your system configuration is correct and free from errors.

!!! Tip

    You can integrate this step into your [Continuous Integration](https://en.wikipedia.org/wiki/Continuous_integration) workflow to ensure that only valid Nix configurations are merged into your codebase.


### Backups

We recommend to set up backups at this point on all machines. 

Please follow our [detailed backup guide](../guides/backups/backup-intro.md) and keep your files safe.


### Migrate Existing Devices

You can [migrate additional existing systems](../guides/migrations/convert-existing-NixOS-configuration.md) into your clan following our extended guides.


