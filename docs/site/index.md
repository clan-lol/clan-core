---
hide:
  - navigation
  - toc
---

# :material-home: What is Clan?

## [Clan](https://clan.lol/) - Peer-to-Peer Computer Management Framework

### Clan is a secure, peer-to-peer framework for managing personal or distributed computing networks

- **Automated** [Secret Management](./guides/secrets.md):

    Effortlessly manage secrets across machines in your network using our automated tools

- **Secure** [mesh VPN connectivity](./guides/mesh-vpn.md):

    Establish encrypted, peer-to-peer communication between machines — without centralized servers.

- **Composable** [Clan Services](./reference/clanServices/index.md):

    Define and deploy reusable service modules that work seamlessly across machines.

- **Custom** [Community services](./guides/services/community.md):

    Everyone can contribute to a growing ecosystem of open-source services.


[Getting Started](./guides/getting-started/index.md){ .md-button }

## :material-book: Guides

**How-to Guides for achieving a certain goal or solving a specific issue.**

<div class="grid cards" markdown>

-   [Create a Machine](./guides/getting-started/add-machines.md)

    ---

    How to create your first machine

-   [macOS](./guides/macos.md)

    ---

    How to manage macOS machines with nix-darwin

-   [Contribute](./guides/contributing/CONTRIBUTING.md)

    ---

    How to set up a development environment

</div>

## Concepts

Explore the foundational ideas.

<div class="grid cards" markdown>

-   [Generators](./concepts/generators.md)

    ---

    Learn about Generators

-   [Inventory](./concepts/inventory.md)

    ---

    Learn about Inventory

</div>

## API Reference

Technical reference for Clan's CLI and Nix modules

<div class="grid cards" markdown>

-   [CLI Reference](./reference/cli/index.md)

    ---

    Command-line interface.

    Full reference for the `clan` CLI tool.

-   [Service Modules](./reference/clanServices/index.md)

    ---

    Overview of built-in service modules that provide composable functionality across machines.

-   [Core NixOS-module](./reference/clan.core/index.md)

    ---

    The foundation of Clan's functionality

    Reference for the `clan-core` NixOS module — automatically part of any machine to enable Clan's core features.

</div>
