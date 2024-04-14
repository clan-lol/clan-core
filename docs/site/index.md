# Getting Started

Welcome to your simple guide on starting a new Clan project.

## What's Inside

We've put together a straightforward guide to help you out:

- [**Starting with a New Clan Project**](#starting-with-a-new-clan-project): Create a new Clan from scratch.
- [**Integrating Clan using Flake-Parts**](getting-started/flake-parts.md)

---

## **Starting with a New Clan Project**

Create your own clan with these initial steps.

### Prerequisites

#### Linux

Clan depends on nix installed on your system. Run the following command to install nix.

```bash
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```

#### NixOS

If you run NixOS the `nix` binary is already installed.

You will also need to enable the `flakes` and `nix-commands` experimental features.

```bash
# /etc/nix/nix.conf or ~/.config/nix/nix.conf
experimental-features = nix-command flakes
```

#### Other

Clan doesn't offer dedicated support for other operating systems yet.

### Step 1: Add Clan CLI to Your Shell

Add the Clan CLI into your development workflow:

```bash
nix shell git+https://git.clan.lol/clan/clan-core#clan-cli
```

### Step 2: Initialize Your Project

Set the foundation of your Clan project by initializing it as follows:

```bash
clan flakes create my-clan
```

This command creates the `flake.nix` and `.clan-flake` files for your project.

### Step 3: Verify the Project Structure

Ensure that all project files exist by running:

```bash
tree
```

This should yield the following:

``` { .console .no-copy }
.
├── flake.nix
├── machines
│   ├── jon
│   │   ├── configuration.nix
│   │   └── hardware-configuration.nix
│   └── sara
│       ├── configuration.nix
│       └── hardware-configuration.nix
└── modules
    └── shared.nix

5 directories, 6 files
```

```bash
clan machines list
```

``` { .console .no-copy }
jon
sara
```

!!! success

    You just successfully bootstrapped your first clan directory.

---

### What's Next?

- [**Machine Configuration**](getting-started/configure.md): Declare behavior and configuration of machines.

- [**Deploy Machines**](getting-started/machines.md): Learn how to deploy to any remote machine.

- [**Installer**](getting-started/installer.md): Setting up new computers remotely is easy with an USB stick.

- [**Check out our Templates**](templates/index.md)

---
