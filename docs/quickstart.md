# Initializing a New Clan Project

## Clone the Clan Template

1. To start a new project, execute the following command to add the clan cli to your shell:

```bash
$ nix shell git+https://git.clan.lol/clan/clan-core
```

2. Than use the following command to clone the clan core template into the current directory:

```
$ clan create .
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

## Modifying the configuration

After cloning the template the next step is to modify the `flake.nix` and follow the instructions in it to add more machines.

---

# Migrating Existing NixOS Configuration Flake

Absolutely, let's break down the migration step by step, explaining each action in detail:

#### Before You Begin

1. **Backup Your Current Configuration**: Always start by making a backup of your current NixOS configuration to ensure you can revert if needed.

   ```shell
   cp -r /etc/nixos ~/nixos-backup
   ```

2. **Update Flake Inputs**: The patch adds a new input named `clan-core` to your `flake.nix`. This input points to a Git repository for Clan Core. Here's the addition:

   ```nix
   inputs.clan-core = {
     url = "git+https://git.clan.lol/clan/clan-core";
     # Don't do this if your machines are on nixpkgs stable.
     inputs.nixpkgs.follows = "nixpkgs";
   };
   ```

   - `url`: Specifies the Git repository URL for Clan Core.
   - `inputs.nixpkgs.follows`: Tells Nix to use the same `nixpkgs` input as your main input (in this case, it follows `nixpkgs`).

3. **Update Outputs**: Then modify the `outputs` section of your `flake.nix` to adapt to Clan Core's new provisioning method. The key changes are as follows:

   Add `clan-core` to the output

   ```diff
   -  outputs = { self, nixpkgs,  }:
   +  outputs = { self, nixpkgs, clan-core }:
   ```

   Previous configuration:

   ```nix
   nixosConfigurations.example-desktop = nixpkgs.lib.nixosSystem {
       system = "x86_64-linux";
       modules = [
           ./configuration.nix
       ];
       [...]
   };
   ```

   After change:

   ```nix
   nixosConfigurations = clan-core.lib.buildClan {
       # this needs to point at the repository root
       directory = self;
       specialArgs = {};
       machines = {
           example-desktop = {
               nixpkgs.hostPlatform = "x86_64-linux";
               imports = [
                   ./configuration.nix
               ];
           };
       };
   };
   ```

   - `nixosConfigurations`: Defines NixOS configurations, using Clan Core’s `buildClan` function to manage the machines.
   - Inside `machines`, a new machine configuration is defined (in this case, `example-desktop`).
   - Inside `example-desktop` which is the target machine hostname, `nixpkgs.hostPlatform` specifies the host platform as `x86_64-linux`.

4. **Rebuild and Switch**: Rebuild your NixOS configuration using the updated flake:

   ```shell
   sudo nixos-rebuild switch --flake .
   ```

   - This command rebuilds and switches to the new configuration. Make sure to include the `--flake .` argument to use the current directory as the flake source.

5. **Test Configuration**: Before rebooting, verify that your new configuration builds without errors or warnings.

6. **Reboot**: If everything is fine, you can reboot your system to apply the changes:

   ```shell
   sudo reboot
   ```

7. **Verify**: After the reboot, confirm that your system is running with the new configuration, and all services and applications are functioning as expected.

By following these steps, you've successfully migrated your NixOS Flake configuration to include the `clan-core` input and adapted the `outputs` section to work with Clan Core's new machine provisioning method.
