## **Migrating Existing NixOS Configuration Flake to Clan Core**

Transitioning your existing setup to Clan Core is straightforward with these detailed steps. Follow this guide to ensure a smooth migration.


### Before You Begin

1. **Backup Your Current Configuration**: Start by creating a backup of your existing NixOS configuration. This step is crucial as it ensures you have the option to revert to your original setup if necessary.

   ```shellSession
   cp -r /etc/nixos ~/nixos-backup
   ```

2. **Initialize flake.nix**: If you haven't yet adopted Nix Flakes in your project, follow these steps to initialize a new `flake.nix` file in your project directory:

   1. **Generate a Trivial flake.nix File**: This creates a basic `flake.nix` file that you can later customize for your project.

      ```bash
      cd /etc/nixos && nix flake init -t github:NixOS/templates#trivial
      ```

   2. **Initialize a Git Repository (if necessary)**: If your project isn't already version-controlled with Git, now is a good time to start. This step initializes a new Git repository in your current directory.

      ```bash
      git init
      ```

   3. **Add Files to the Repository**: Add your project files to the Git repository. This step is essential for nix flakes as it will ignore files not inside the git repo. 

      ```bash
      git add .
      ```

1. **Update Flake Inputs**: Introduce a new input in your `flake.nix` for the Clan Core dependency:

   ```nix
   inputs.clan-core = {
     url = "git+https://git.clan.lol/clan/clan-core";
     inputs.nixpkgs.follows = "nixpkgs"; # Only if your configuration uses nixpkgs stable.
   };
   ```

   Ensure to replace the placeholder URL with the actual Git repository URL for Clan Core. The `inputs.nixpkgs.follows` line indicates that your flake should use the same `nixpkgs` input as your main flake configuration.

2. **Update Outputs**: Modify the `outputs` section of your `flake.nix` to accommodate Clan Core's provisioning method:

   ```diff
   -  outputs = { self, nixpkgs }: {
   +  outputs = { self, nixpkgs, clan-core }:
   ```

3. **Revise System Build Function**: Transition from using `lib.nixosSystem` to `clan-core.lib.buildClan` for building your machine derivations:

   - Previously:

     ```nix
     outputs = { self, nixpkgs }: {
      nixosConfigurations.example-desktop = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [ ./configuration.nix ];
      };
     }
     ```

   - With Clan Core:

     ```nix
     outputs = { self, nixpkgs, clan-core }:
      let clan = clan-core.lib.buildClan {
        directory = self; # Point this to the repository root.
        clanName = "__CHANGE_ME__"; # Ensure this is internet wide unique.
        machines = {
          example-desktop = {
            nixpkgs.hostPlatform = "x86_64-linux";
            imports = [ ./configuration.nix ];
          };
        };
      };
     in { inherit (clan) nixosConfigurations clanInternals; };
     ```

4. **Rebuild and Switch**: Apply your updated configuration:

   ```shellSession
   sudo nixos-rebuild switch --flake /etc/nixos
   ```

   This rebuilds your system configuration and switches to it. The `--flake .` argument specifies that the current directory's flake should be used.

5. **Test Configuration**: Ensure your new configuration builds correctly without any errors or warnings before proceeding.

6. **Reboot**: If the build is successful and no issues are detected, reboot your system:

   ```shellSession
   sudo reboot
   ```

7. **Verify**: After rebooting, verify that your system operates with the new configuration and that all services and applications are functioning as expected.


## What's next

After creating your flake, you can check out how to add [new machines](./machines.md)

---


## Integrating Clan with Flakes using Flake-Parts

Clan supports integration with the Nix ecosystem through its flake module, making it compatible with [flake.parts](https://flake.parts/),
a tool for modular Nix flakes composition.
Here's how to set up Clan using flakes and flake-parts.

### 1. Update Your Flake Inputs

To begin, you'll need to add `clan-core` as a new dependency in your flake's inputs. This is alongside the already existing dependencies, such as `flake-parts` and `nixpkgs`. Here's how you can update your `flake.nix` file:



```nix
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-parts.url = "github:hercules-ci/flake-parts";
  inputs.flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";

  # Newly added
  inputs.clan-core.url = "git+https://git.clan.lol/clan/clan-core";
  inputs.clan-core.inputs.nixpkgs.follows = "nixpkgs";
  inputs.clan-core.inputs.flake-parts.follows = "flake-parts";
```

### 2. Import Clan-Core Flake Module

After updating your flake inputs, the next step is to import the `clan-core` flake module into your project. This allows you to utilize Clan functionalities within your Nix project. Update your `flake.nix` file as shown below:

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

Lastly, define your Clan configuration settings, including a unique clan name and the machines you want to manage with Clan.
This is where you specify the characteristics of each machine,
such as the platform and specific Nix configurations. Update your `flake.nix` like this:

```nix
  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (
      {
        imports = [
          inputs.clan-core.flakeModules.default
        ];
        clan = {
          clanName = "NEEDS_TO_BE_UNIQUE"; # Please replace this with a unique name for your clan.
          directory = inputs.self;
          machines = {
            example-desktop = {
              nixpkgs.hostPlatform = "x86_64-linux";
              imports = [ ./configuration.nix ];
            };
          };
        };
      }
    );
```

For detailed information about configuring `flake-parts` and the available options within Clan,
refer to the Clan module documentation located [here](https://git.clan.lol/clan/clan-core/src/branch/main/flakeModules/clan.nix).

### **Next Steps**
With your flake created, explore how to add new machines by reviewing the documentation provided [here](./machines.md).

---