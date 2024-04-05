# **Quick Start Guide to Initializing a New Clan Project**

This guide will lead you through initiating a new Clan project

## **Overview**

Dive into our structured guide tailored to meet your needs:

- [**Starting with a New Clan Project**](#starting-with-a-new-clan-project): Kickstart your journey with Clan by setting up a new project from the ground up.
- [**Migrating Existing Flake Configuration**](migrate.md#migrating-existing-nixos-configuration-flake): Transition your existing flake-based Nix configuration to harness the power of Clan Core.
- [**Integrating Clan using Flake-Parts**](./migrate.md#integrating-clan-with-flakes-using-flake-parts): Enhance your Clan experience by integrating it with Flake-Parts.

---

## **Starting with a New Clan Project**

Embark on your Clan adventure with these initial steps:

### **Step 1: Add Clan CLI to Your Shell**
Incorporate the Clan CLI into your development workflow with this simple command:
```shell
nix shell git+https://git.clan.lol/clan/clan-core
```

### **Step 2: Initialize Your Project**
Set the foundation of your Clan project by initializing it as follows:
```shell
clan flakes create my-clan
```
This command crafts the essential `flake.nix` and `.clan-flake` files for your project.

### **Step 3: Verify the Project Structure**
Ensure the creation of your project files with a quick directory listing:
```shell
cd my-clan && ls -la
```
Look for `.clan-flake`, `flake.lock`, and `flake.nix` among your files to confirm successful setup.

### **Understanding `.clan-flake`**
The `.clan-flake` file, while optional, is instrumental in helping the Clan CLI identify your project's root directory, easing project management.

### **Next Steps**
Ready to expand? Explore how to add new machines to your project with the helpful documentation [here](./machines.md).

---
