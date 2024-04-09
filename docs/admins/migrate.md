# Migrating Existing NixOS Configuration Flake to Clan Core

Transitioning your existing setup to Clan Core is easy and straightforward. Follow this guide to ensure a smooth migration.

## 0. Prerequisites

### Backup Your Current Configuration

Create a backup of your existing NixOS configuration.
This step ensures you have the option to revert to your original setup if necessary.

```bash
cp -r /etc/nixos ~/nixos-backup
```

## 1. Initialize a flake.nix

If you haven't yet adopted Nix Flakes in your project, follow these steps to initialize a new `flake.nix` file in your project directory.

> Note: Clan is based on flakes, it is possible to use Clan without flakes but not officially supported yet.

### Generate a Trivial flake.nix File

This creates a basic `flake.nix` file that you can later customize for your project.
  
Create a place for your system configuration if you don't have one already. We'll create `~/clans/empire`.
In this example, we're setting up a directory named `empire` inside a `clans` folder in your home directory. This is just an example, and you can name and place your project directory as it suits your organizational preferences.

```bash
mkdir -p ~/clans/empire && cd ~/clans/empire 
nix flake init -t github:NixOS/templates#trivial
```

This will initialize a `flake.nix` file that looks like this:

```nix
# flake.nix
{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }: {

    packages.x86_64-linux.hello = nixpkgs.legacyPackages.x86_64-linux.hello;

    packages.x86_64-linux.default = self.packages.x86_64-linux.hello;

  };
}
```

### Initialize a Git Repository (optional/recommended)

If your project isn't already version-controlled with Git, now is a good time to start. This step initializes a new Git repository in your current directory.

```bash
git init && git add .
```

> Note: adding all files to the git index is essential for `nix flakes` as `flakes` ignores source files that are not part of the git index.

Confirm your flake repository is working:

```bash
nix flake show
```

```bash
warning: creating lock file flake.lock'
path: <some/hash> 
└───packages
    └───x86_64-linux
        ├───default: package 'hello-2.12.1'
        └───hello: package 'hello-2.12.1'
```

## 2. Create your first Machine

Create a directory where you put **all machine specific configs** like the `configuration.nix` or `hardware-configuration.nix`

> Following this structure will allow you nicely organize all your different machines and allows the Clan-CLI to automatically detect and manage your machines.

```bash
mkdir -p machines/jons-desktop
```

> In this case `jons-desktop` is the hostname of the machine you want to manage with Clan.

Move your `configuration.nix` and included files into `machines/jons-desktop`

```bash
mv configuration.nix machines/jons-desktop/configuration.nix 
```

Git add all new files/folders

```bash
git add machines
```

### Migrate to flakes and `buildClan`

Add `Clan Core` as a new input to your `flake.nix`:

```nix
# flake.nix
inputs.clan-core = {
  url = "git+https://git.clan.lol/clan/clan-core";
  inputs.nixpkgs.follows = "nixpkgs"; # Needed if your configuration uses nixpkgs unstable.
}
```

Your flake should now look something like this.

```nix
# flake.nix
{
  inputs = {
    # Change ref to your liking
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";

    clan-core = {
      url = "git+https://git.clan.lol/clan/clan-core";
      inputs.nixpkgs.follows = "nixpkgs"; # Needed if your configuration uses nixpkgs unstable.
    };
  };

  outputs = { self, nixpkgs, clan-core }: {
  # ...
  };
}
```

> Note: `inputs.nixpkgs.follows` ensures that `clan-core` uses the same `nixpkgs` version as the rest of your flake.

### Use `clan-core.lib.buildClan` for declaring your machines

If you used flakes already you might use `lib.nixosSystem`

```nix
# OLD

# flake.nix
outputs = { self, nixpkgs }: {
  nixosConfigurations.jons-desktop = nixpkgs.lib.nixosSystem {
    system = "x86_64-linux";
    modules = [ ./configuration.nix ];
  };
}
```

We explain how to setup `buildClan`

```nix
# flake.nix
outputs = { self, nixpkgs, clan-core }:
  let 
    clan = clan-core.lib.buildClan {
      ## Clan wide settings. (Required)
      clanName = "__CHANGE_ME__"; # Ensure to choose a unique name.
      directory = self; # Point this to the repository root.

      specialArgs = { }; # Add arguments to every nix import in here
      machines = {
        jons-desktop = {
          nixpkgs.hostPlatform = "x86_64-linux";
          imports = [
            ./machines/jons-desktop/configuration.nix
            clan-core.clanModules.sshd # Add openssh server forcLanmanagement
          ];
        };
      };
    };
  in
  { 
    inherit (clan) nixosConfigurations clanInternals; 
  };
```

## Rebuild and Switch

Apply your updated configuration

Before we can rebuild the system we should replace the source of your system ( folder `/etc/nixos`) with a symlink to the `repo`

```bash
sudo ls -s ~/clans/empire /etc/nixos
```

```bash
sudo nixos-rebuild switch
```

This rebuilds your system configuration and switches to it.

> Note: nixos-rebuild switch uses /etc/nixos by default.

## Finish installation

- **Test Configuration**: Ensure your new configuration builds correctly without any errors or warnings before proceeding.
- **Reboot**: If the build is successful and no issues are detected, reboot your system:

  ```shellSession
  sudo reboot
  ```

- **Verify**: After rebooting, verify that your system operates with the new configuration and that all services and applications are functioning as expected.

---

## What's next?

After creating your Clan see [managing machines](./machines.md)

Or continue with **flake-parts integration**

## Integrating Clan with Flakes using `flake-parts`

Clan supports integration with [flake.parts](https://flake.parts/) a tool which allows modular compositions.

Here's how to set up Clan using flakes and flake-parts.

### 1. Update Your Flake Inputs

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

### 2. Import Clan-Core Flake Module

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

With your flake created, explore how to add new machines by reviewing the documentation provided [here](./machines.md).

---

## TODO

* How do I use Clan machines install to setup my current machine?
* I probably need the clan-core sshd module for that?
* We need to tell them that configuration.nix of a machine NEEDS to be under the directory CLAN_ROOT/machines/<machine-name> I think?