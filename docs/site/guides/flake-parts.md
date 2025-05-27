
Clan supports integration with [flake-parts](https://flake.parts/), a framework for constructing your `flake.nix` using modules.

To construct your Clan using flake-parts, follow these steps:

## 1. Update Your Flake Inputs

To begin, you'll need to add `flake-parts` as a new dependency in your flake's inputs. This is alongside the already existing dependencies, such as `clan-core` and `nixpkgs`. Here's how you can update your `flake.nix` file:

```nix
# flake.nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs?ref=nixos-unstable";

  # New flake-parts input
  flake-parts.url = "github:hercules-ci/flake-parts";
  flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";

  clan-core = {
    url = "git+https://git.clan.lol/clan/clan-core";
    inputs.nixpkgs.follows = "nixpkgs"; # Don't do this if your machines are on nixpkgs stable.
    # New
    inputs.flake-parts.follows = "flake-parts";
  };
}
```

## 2. Import the Clan flake-parts Module

After updating your flake inputs, the next step is to import the Clan flake-parts module. This will make the [Clan options](../reference/nix-api/buildclan.md) available within `mkFlake`.

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

### 3. Configure Clan Settings and Define Machines

Next you'll need to configure Clan wide settings and define machines, here's an example of how `flake.nix` should look:

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
      # See: https://docs.clan.lol/reference/nix-api/buildclan/
      clan = {
        # Clan wide settings
        meta.name = ""; # This is required and must be unique

        machines = {
          jon = {
            imports = [
              ./modules/firefox.nix
              # ... more modules
            ];

            nixpkgs.hostPlatform = "x86_64-linux";

            # Set this for Clan commands to work remotely over SSH like `clan machines update`
            clan.core.networking.targetHost = "root@jon";

            # remote> lsblk --output NAME,ID-LINK,FSTYPE,SIZE,MOUNTPOINT
            disko.devices.disk.main = {
              device = "/dev/disk/by-id/nvme-eui.e8238fa6bf530001001b448b4aec2929";
            };
          };
        };
      };
    });
}
```

For detailed information about configuring `flake-parts` and the available options within Clan,
refer to the Clan module documentation located [here](https://git.clan.lol/clan/clan-core/src/branch/main/flakeModules/clan.nix).

---
