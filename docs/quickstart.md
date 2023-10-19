# Initializing a New Clan Project

## Create a new flake

1. To start a new project, execute the following command to add the clan cli to your shell:

```shellSession
$ nix shell git+https://git.clan.lol/clan/clan-core
```

2. Then use the following commands to initialize a new clan-flake:

```shellSession
$ clan flake create my-clan
```

This action will generate two primary files: `flake.nix` and `.clan-flake`.

```shellSession
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

## What's next

After creating your flake, you can check out how to add [new machines](./machines.md)

---

# Migrating Existing NixOS Configuration Flake

Absolutely, let's break down the migration step by step, explaining each action in detail:

#### Before You Begin

1. **Backup Your Current Configuration**: Always start by making a backup of your current NixOS configuration to ensure you can revert if needed.

   ```shellSession
   $ cp -r /etc/nixos ~/nixos-backup
   ```

2. **Update Flake Inputs**: Add a new input for the `clan-core` dependency:

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
   {
       nixosConfigurations.example-desktop = nixpkgs.lib.nixosSystem {
           system = "x86_64-linux";
           modules = [
               ./configuration.nix
           ];
           [...]
       };
   }
   ```

   After change:

   ```nix
   let clan = clan-core.lib.buildClan {
       # this needs to point at the repository root
       directory = self;
       specialArgs = {};
       clanName = "NEEDS_TO_BE_UNIQUE"; # TODO: Changeme
       machines = {
           example-desktop = {
               nixpkgs.hostPlatform = "x86_64-linux";
               imports = [
                   ./configuration.nix
               ];
           };
       };
   };
   in { inherit (clan) nixosConfigurations clanInternals; }
   ```

   - `nixosConfigurations`: Defines NixOS configurations, using Clan Core’s `buildClan` function to manage the machines.
   - Inside `machines`, a new machine configuration is defined (in this case, `example-desktop`).
   - Inside `example-desktop` which is the target machine hostname, `nixpkgs.hostPlatform` specifies the host platform as `x86_64-linux`.
   - `clanInternals`: Is required to enable evaluation of the secret generation/upload script on every architecture
   - `clanName`: Is required and needs to be globally unique, as else we have a cLAN name clash

4. **Rebuild and Switch**: Rebuild your NixOS configuration using the updated flake:

   ```shellSession
   $ sudo nixos-rebuild switch --flake .
   ```

   - This command rebuilds and switches to the new configuration. Make sure to include the `--flake .` argument to use the current directory as the flake source.

5. **Test Configuration**: Before rebooting, verify that your new configuration builds without errors or warnings.

6. **Reboot**: If everything is fine, you can reboot your system to apply the changes:

   ```shellSession
   $ sudo reboot
   ```

7. **Verify**: After the reboot, confirm that your system is running with the new configuration, and all services and applications are functioning as expected.

By following these steps, you've successfully migrated your NixOS Flake configuration to include the `clan-core` input and adapted the `outputs` section to work with Clan Core's new machine provisioning method.

## What's next

After creating your flake, you can check out how to add [new machines](./machines.md)
