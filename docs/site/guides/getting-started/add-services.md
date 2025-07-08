# How to add services

A service in clan is a self-contained, reusable unit of system configuration that provides a specific piece of functionality across one or more machines.

Think of it as a recipe for running a tool — like automatic backups, VPN networking, monitoring, etc.

In Clan Services are multi-Host & role-based:

- Roles map machines to logical service responsibilities, enabling structured, clean deployments.

- You can use tags instead of explicit machine names.

To learn more: [Guide about clanService](../clanServices.md)

!!! Important
    It is recommended to add at least one networking service such as `zerotier` that allows to reach all your clan machines from your setup computer across the globe.

## Configure a Zerotier Network (recommended)

```{.nix title="flake.nix" hl_lines="20-28"}
{
    inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
    inputs.nixpkgs.follows = "clan-core/nixpkgs";
    inputs.flake-parts.follows = "clan-core/flake-parts";
    inputs.flake-parts.inputs.nixpkgs-lib.follows = "clan-core/nixpkgs";

    outputs =
        inputs@{ flake-parts, ... }:
        flake-parts.lib.mkFlake { inherit inputs; } {
            imports = [ inputs.clan-core.flakeModules.default ];
            # Sometimes this attribute set is defined in clan.nix
            clan = {
                inventory.machines = {
                    jon = {
                        targetHost = "root@jon";
                    };
                    sara = {
                        targetHost = "root@jon";
                    };
                };
                inventory.instances = {
                    zerotier = { # (1)
                        # Defines 'jon' as the controller
                        roles.controller.machines.jon = {};
                        # Defines all machines as networking peer.
                        # The 'all' tag is a clan builtin.
                        roles.peer.tags.all = {};
                    };
                }
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

1. See [reference/clanServices](../../reference/clanServices/index.md) for all available services and how to configure them.
   Or read [authoring/clanServices](../authoring/clanServices/index.md) if you want to bring your own

## Adding more recommended defaults

Adding the following services is recommended for most users:

```{.nix title="flake.nix" hl_lines="25-35"}
{
    inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
    inputs.nixpkgs.follows = "clan-core/nixpkgs";
    inputs.flake-parts.follows = "clan-core/flake-parts";
    inputs.flake-parts.inputs.nixpkgs-lib.follows = "clan-core/nixpkgs";

    outputs =
        inputs@{ flake-parts, ... }:
        flake-parts.lib.mkFlake { inherit inputs; } {
            imports = [ inputs.clan-core.flakeModules.default ];
            # Sometimes this attribute set is defined in clan.nix
            clan = {
                inventory.machines = {
                    jon = {
                        targetHost = "root@jon";
                    };
                    sara = {
                        targetHost = "root@jon";
                    };
                };
                inventory.instances = {
                    zerotier = {
                        roles.controller.machines.jon = {};
                        roles.peer.tags.all = {};
                    };
                    admin = { # (1)
                        roles.default.tags.all = { };
                        roles.default.settings = {
                            allowedKeys = {
                                "my-user" = "ssh-ed25519 AAAAC3N..."; # elided
                            };
                        };
                    };
                    state-version = { # (2)
                        roles.default.tags.all = { };
                    };
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

1. The `admin` service will generate a **root-password** and **add your ssh-key** that allows for convienient administration.

2. The `state-version` service will generate a [nixos state version](https://wiki.nixos.org/wiki/FAQ/When_do_I_update_stateVersion) for each system once it is deployed.