# How to add machines

Machines can be added using the following methods

- Editing nix expressions in flake.nix (i.e. via `clan-core.lib.clan`)
- Editing machines/`machine_name`/configuration.nix (automatically included if it exists)
- `clan machines create` (imperative)

See the complete [list](../../guides/more-machines.md#automatic-registration) of auto-loaded files.

## Create a machine

=== "CLI (imperative)"

    ```sh
    clan machines create jon
    ```

    The imperative command might create a machine folder in `machines/jon`
    And might persist information in `inventory.json`

=== "flake.nix (flake-parts)"

    ```{.nix hl_lines=12-15}
    {
        inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
        inputs.nixpkgs.follows = "clan-core/nixpkgs";
        inputs.flake-parts.follows = "clan-core/flake-parts";
        inputs.flake-parts.inputs.nixpkgs-lib.follows = "clan-core/nixpkgs";

        outputs =
            inputs@{ flake-parts, ... }:
            flake-parts.lib.mkFlake { inherit inputs; } {
                imports = [ inputs.clan-core.flakeModules.default ];
                clan = {
                    inventory.machines = {
                        # Define a machine
                        jon = { };
                    };
                };

                systems = [
                    "x86_64-linux"
                    "aarch64-linux"
                    "x86_64-darwin"
                    "aarch64-darwin"
                ];
        };
    }
    ```

=== "flake.nix (classic)"

    ```{.nix hl_lines=11-14}
    {
        inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
        inputs.nixpkgs.follows = "clan-core/nixpkgs";

        outputs =
            { self, clan-core, ... }:
            let
                clan = clan-core.lib.clan {
                    inherit self;

                    inventory.machines = {
                        # Define a machine
                        jon = { };
                    };
                };
            in
            {
                inherit (clan.config)
                    nixosConfigurations
                    nixosModules
                    clanInternals
                    darwinConfigurations
                    darwinModules
                    ;
            };
    }
    ```

### Configuring a machine

Inside of the `flake.nix` file:

```nix title="flake.nix"
clan {
    inventory.machines = {
        jon = {
            # Define targetHost here
            # Required before deployment
            deploy.targetHost = "root@ip";
            # Define tags here
            tags = [ "desktop" "backup" ];
        };
    };
}
```


```nix title="flake.nix"
clan {
    # Define additional nixosConfiguration here
    # Or in /machines/jon/configuration.nix (autoloaded)
    machines = {
        jon = { config, pkgs, ... }: {
            environment.systemPackages = with pkgs; [ firefox ];
        };
    };
}
```

### (Optional): Renaming Machine

For renaming jon to your own machine name, you can use the following command:

```
git mv ./machines/jon ./machines/newname
```

Note that our clan lives inside a git repository.
Only files that have been added with `git add` are recognized by `nix`.
So for every file that you add or rename you also need to run:

```
git add ./path/to/my/file
```

### (Optional): Removing a Machine

If you only want to setup a single machine at this point, you can delete `sara` from `flake.nix` as well as from the machines directory:

```
git rm -rf ./machines/sara
```
