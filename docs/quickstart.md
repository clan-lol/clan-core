# Initializing a New Clan Project

## Clone the Clan Template

To start a new project, execute the following command to clone the Clan Core template:

```bash
$ nix flake init -t git+https://git.clan.lol/clan/clan-core
```

This action will generate two primary files: `flake.nix` and `.clan-flake`.

```bash
$ ls -la
drwx------ joerg users   5 B  a minute ago   ./
drwxrwxrwt root  root  139 B  12 seconds ago ../
.rw-r--r-- joerg users  77 B  a minute ago   .clan-flake
.rw-r--r-- joerg users 4.8 KB a minute ago   flake.lock
.rw-r--r-- joerg users 242 B  a minute ago   flake.nix
```

### Understanding the .clan-flake Marker File

The `.clan-flake` marker file serves an optional purpose: it helps the `clan-cli` utility locate the project's root directory.
If `.clan-flake` is missing, `clan-cli` will instead search for other indicators like `.git`, `.hg`, `.svn`, or `flake.nix` to identify the project root.

---

# Migrating Existing NixOS Configuration Flake

## Integrating with Existing NixOS Machines

If you already manage NixOS machines using a flake, you can integrate them with the Clan Core as shown in the example below:

```nix
{
  description = "My custom NixOS flake";

  inputs.clan-core.url = "git+https://git.clan.lol/clan/clan-core";

  outputs = { clan-core, ... }: {
    nixosConfigurations = clan-core.lib.buildClan {
      directory = ./.;
      machines = {
        turingmachine = {
          nixpkgs.pkgs = nixpkgs.legacyPackages.aarch64-linux;
          imports = [
            ./configuration.nix
          ];
        };
      };
    };
  };
}
```

In this configuration:

- `description`: Provides a brief description of the flake.
- `inputs.clan-core.url`: Specifies the Clan Core template's repository URL.
- `nixosConfigurations`: Defines NixOS configurations, using Clan Core's `buildClan` function to manage the machines.
