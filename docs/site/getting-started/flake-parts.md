# Clan with `flake-parts`

Clan supports integration with [flake.parts](https://flake.parts/) a tool which allows modular compositions.

Here's how to set up Clan using flakes and flake-parts.

## 1. Update Your Flake Inputs

To begin, you'll need to add `flake-parts` as a new dependency in your flake's inputs. This is alongside the already existing dependencies, such as `flake-parts` and `nixpkgs`. Here's how you can update your `flake.nix` file:

```nix
# flake.nix
inputs = {
  nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";

  # New flake-parts input
  flake-parts.url = "github:hercules-ci/flake-parts";
  flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";
  
  clan-core = {
    url = "git+https://git.clan.lol/clan/clan-core";
    inputs.nixpkgs.follows = "nixpkgs"; # Needed if your configuration uses nixpkgs unstable.
    # New
    inputs.flake-parts.follows = "flake-parts";
  };
}
```

## 2. Import Clan-Core Flake Module

After updating your flake inputs, the next step is to import the `clan-core` flake module. This will make the [clan options](https://git.clan.lol/clan/clan-core/src/branch/main/flakeModules/clan.nix) available within `mkFlake`.

```nix
  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (
      {
        imports = [
          inputs.clan-core.flakeModules.default
        ];
      }
    );
```

### 3. Configure Clan Settings and Define Machines

Configure your clan settings and define machine configurations.

Below is a guide on how to structure this in your flake.nix:

```nix
  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (
      {
        imports = [
          inputs.clan-core.flakeModules.default
        ];
        clan = {
          ## Clan wide settings. (Required)
          clanName = "__CHANGE_ME__"; # Ensure to choose a unique name.
          directory = self; # Point this to the repository root.

          specialArgs = { }; # Add arguments to every nix import in here
          
          machines = {
            jons-desktop = {
              nixpkgs.hostPlatform = "x86_64-linux";
              imports = [
                clan-core.clanModules.sshd # Add openssh server for Clan management
                ./configuration.nix
              ];
            };
          };
        };
      }
    );
```

For detailed information about configuring `flake-parts` and the available options within Clan,
refer to the Clan module documentation located [here](https://git.clan.lol/clan/clan-core/src/branch/main/flakeModules/clan.nix).

### Next Steps

With your flake created, explore how to add new machines by reviewing the documentation provided [here](machines.md).

---

## TODO

* How do I use Clan machines install to setup my current machine?
* I probably need the clan-core sshd module for that?
* We need to tell them that configuration.nix of a machine NEEDS to be under the directory CLAN_ROOT/machines/<machine-name> I think?
