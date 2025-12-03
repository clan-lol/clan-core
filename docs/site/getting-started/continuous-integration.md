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

