# How to add machines

Machines can be added using the following methods

- Editing nix expressions in flake.nix (i.e. via `clan-core.lib.clan`)
- Editing machines/`machine_name`/configuration.nix (automatically included if it exists)
- `clan machines create` (imperative)

See the complete [list](../../guides/more-machines.md#automatic-registration) of auto-loaded files.

## Create a machine

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

=== "CLI (imperative)"

    ```sh
    clan machines create jon
    ```

    The imperative command might create a machine folder in `machines/jon`
    And might persist information in `inventory.json`


### Configuring a machine

!!! Note
    The option: `inventory.machines.<name>` is used to define metadata about the machine
    That includes for example `deploy.targethost` `machineClass` or `tags`

    The option: `machines.<name>` is used to add extra *nixosConfiguration* to a machine

```{.nix .annotate title="flake.nix" hl_lines="3-13 18-22"}
# Sometimes this attribute set is defined in clan.nix
clan = {
    inventory.machines = {
        jon = {
            # Define targetHost here
            # Required before deployment
            deploy.targetHost = "root@jon"; # (1)
            # Define tags here
            tags = [ ];
        };
        sara = {
            deploy.targetHost = "root@sara";
            tags = [ ];
        };
    };
    # Define additional nixosConfiguration here
    # Or in /machines/jon/configuration.nix (autoloaded)
    machines = {
        jon = { config, pkgs, ... }: {
            users.users.root.openssh.authorizedKeys.keys = [
                "ssh-ed25519 AAAAC3NzaC..." # elided (2)
            ];
        };
    };
}
```

1. It is required to define a *targetHost* for each machine before deploying. Best practice has been, to use the zerotier ip/hostname or the ip from the from overlay network you decided to use.
2. Add your *ssh key* here - That will ensure you can always login to your machine via *ssh* in case something goes wrong.

### (Optional) Renaming a Machine

Older templates included static machine folders like `jon` and `sara`.
If your setup still uses such static machines, you can rename a machine folder to match your own machine name:

```bash
git mv ./machines/jon ./machines/<your-machine-name>
```

Since your Clan configuration lives inside a Git repository, remember:

* Only files tracked by Git (`git add`) are recognized.
* Whenever you add, rename, or remove files, run:

```bash
git add ./machines/<your-machine-name>
```

to stage the changes.

---

### (Optional) Removing a Machine

If you want to work with a single machine for now, you can remove other machine entries both from your `flake.nix` and from the `machines` directory. For example, to remove the machine `sara`:

```bash
git rm -rf ./machines/sara
```

Make sure to also remove or update any references to that machine in your `nix files` or `inventory.json` if you have any of that
