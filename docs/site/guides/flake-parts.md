Clan supports integration with [flake-parts](https://flake.parts/), a framework for constructing your `flake.nix` using modules. Follow these steps to integrate Clan with flake-parts:

## Step 1: Update Your Flake Inputs

Add `flake-parts` as a dependency in your `flake.nix` file alongside existing dependencies like `clan-core` and `nixpkgs`. Here's an example:

```nix
# flake.nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs?ref=nixos-unstable";

  # Add flake-parts
  flake-parts.url = "github:hercules-ci/flake-parts";
  flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";

  clan-core = {
    url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
    inputs.nixpkgs.follows = "nixpkgs"; # Avoid this if using nixpkgs stable.
    inputs.flake-parts.follows = "flake-parts"; # New
  };
};
```

## Step 2: Import the Clan flake-parts Module

Next, import the Clan flake-parts module to make the [Clan options](../reference/options/clan.md) available within `mkFlake`:

```nix
{
  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (
      {
        imports = [
          inputs.clan-core.flakeModules.default
        ];
      }
    );
}
```

## Step 3: Configure Clan Settings and Define Machines

Configure Clan-wide settings and define machines. Here's an example `flake.nix`:

```nix
{
  outputs = inputs@{ flake-parts, clan-core, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } ({self, pkgs, ...}: {
      # See: https://flake.parts/getting-started
      systems = [
        "x86_64-linux"
      ];

      # Import the Clan flake-parts module
      imports = [
        clan-core.flakeModules.default
      ];

      # Define your Clan
      clan = {
        meta.name = ""; # Required and must be unique
        meta.tld = ""; # Required and must be unique

        machines = {
          jon = {
            imports = [
              ./modules/firefox.nix
              # Add more modules as needed
            ];

            nixpkgs.hostPlatform = "x86_64-linux";

            # Enable remote Clan commands over SSH
            clan.core.networking.targetHost = "root@jon";

            # Disk configuration
            disko.devices.disk.main = {
              device = "/dev/disk/by-id/nvme-eui.e8238fa6bf530001001b448b4aec2929";
            };
          };
        };
      };
    });
}
```

For more details on configuring `flake-parts` and available Clan options, refer to the [Clan module documentation](https://git.clan.lol/clan/clan-core/src/branch/main/flakeModules/clan.nix).
