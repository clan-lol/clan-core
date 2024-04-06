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


3. **Create Machines Directory**: Create a machines directory where you put all machine specific nix configs like the configuration.nix
    1. Create the machines directory in your git root example: `/etc/nixos/machines/`
        ```bash
        mkdir machines
        ```

    2. Inside the machines directory create a directory named after the hostname of the machine you want to manage with clan.
        ```bash
        mkdir machines/jons-desktop
        ```

    3. Move your `configuration.nix` and included files into  `machines/jons-desktop`
        ```bash
        mv configuration.nix machines/jons-desktop/configuration.nix 
        ```

    4. Git add your new machines folder
        ```bash
        git add machines
        ```

4. **Update Flake Inputs**: Introduce a new input in your `flake.nix` for the Clan Core dependency:

   ```nix
   inputs.clan-core = {
     url = "git+https://git.clan.lol/clan/clan-core";
     inputs.nixpkgs.follows = "nixpkgs"; # Only if your configuration uses nixpkgs unstable.
   };
   ```

   Ensure to replace the placeholder URL with the actual Git repository URL for Clan Core. The `inputs.nixpkgs.follows` line indicates that your flake should use the same `nixpkgs` input as your main flake configuration.


5. **Revise System Build Function**: Transition from using `lib.nixosSystem` to `clan-core.lib.buildClan` for building your machine derivations:

   - Previously:

     ```nix
     outputs = { self, nixpkgs }: {
      nixosConfigurations.jons-desktop = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [ ./configuration.nix ];
      };
     };
     ```

   - With Clan Core:

     ```nix
     outputs = { self, nixpkgs, clan-core }:
      let clan = clan-core.lib.buildClan {
        specialArgs = { }; # Add arguments to every nix import in here
        directory = self; # Point this to the repository root.
        clanName = "__CHANGE_ME__"; # Ensure this is internet wide unique.
        machines = {
          jons-desktop = {
            nixpkgs.hostPlatform = "x86_64-linux";
            imports = [
              clan-core.clanModules.sshd # Add openssh server for clan management
              ./machines/jons-desktop/configuration.nix
            ];
          };
        };
      };
     in { inherit (clan) nixosConfigurations clanInternals; };
     ```



6. **Rebuild and Switch**: Apply your updated configuration:

   ```shellSession
   sudo nixos-rebuild switch --flake /etc/nixos
   ```

   This rebuilds your system configuration and switches to it. The `--flake /etc/nixos` argument specifies that the `/etc/nixos` directory's flake should be used.

7. **Test Configuration**: Ensure your new configuration builds correctly without any errors or warnings before proceeding.

8. **Reboot**: If the build is successful and no issues are detected, reboot your system:

   ```shellSession
   sudo reboot
   ```

9. **Verify**: After rebooting, verify that your system operates with the new configuration and that all services and applications are functioning as expected.


# TODO:
* How do I use clan machines install to setup my current machine?
* I probably need the clan-core sshd module for that?
* We need to tell them that configuration.nix of a machine NEEDS to be under the directory CLAN_ROOT/machines/<machine-name> I think?


## What's next

After creating your clan checkout [managing machines](./machines.md)

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
          specialArgs = { }; # Add arguments to every nix import in here
          clanName = "__CHANGE_ME__"; # Ensure this is internet wide unique.
          directory = inputs.self;
          machines = {
            jons-desktop = {
              nixpkgs.hostPlatform = "x86_64-linux";
              imports = [
                clan-core.clanModules.sshd # Add openssh server for clan management
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

### **Next Steps**
With your flake created, explore how to add new machines by reviewing the documentation provided [here](./machines.md).

---