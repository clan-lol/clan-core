# Managing macOS Machines with Clan

This guide explains how to manage macOS machines using Clan.

## Supported Features

Currently, Clan supports the following features for macOS:

- `clan machines update` for existing [nix-darwin](https://github.com/nix-darwin/nix-darwin) installations
- Support for [vars](./vars/vars-overview.md)

## Add Your Machine to Your Clan Flake

In this example, we'll name the machine `yourmachine`. Replace this with your preferred machine name.

=== "**If using clan-core.lib.clan**"

```nix
clan-core.lib.clan {
    inventory = {
        machines.yourmachine.machineClass = "darwin";
    };
}
```

=== "**If using flake-parts**"

```nix
{
  clan = {
    inventory = {
        machines.yourmachine.machineClass = "darwin";
    };
  };
}
```

## Add a `configuration.nix` for Your Machine

Create the file `./machines/yourmachine/configuration.nix` with the following content (replace `yourmachine` with your chosen machine name):

```nix
{
  clan.core.networking.targetHost = "root@ip_or_hostname";
  nixpkgs.hostPlatform = "aarch64-darwin"; # Use "x86_64-darwin" for Intel-based Macs
}
```

After creating the file, run `git add` to ensure Nix recognizes it.

## Generate Vars (If Needed)

If your machine uses vars, generate them with:

```
clan vars generate yourmachine
```

Replace `yourmachine` with your chosen machine name.

## Install Nix

Install Nix on your macOS machine using one of the methods described in the [nix-darwin prerequisites](https://github.com/nix-darwin/nix-darwin?tab=readme-ov-file#prerequisites).


## Install nix-darwin

Upload your Clan flake to the macOS machine. Then, from within your flake directory, run:

```sh
sudo nix run nix-darwin/master#darwin-rebuild -- switch --flake .#yourmachine
```

Replace `yourmachine` with your chosen machine name.

## Manage Your Machine with Clan

Once all the steps above are complete, you can start managing your machine with:

```
clan machines update yourmachine
```

This command can be run from any computer that can reach this machine via SSH.
