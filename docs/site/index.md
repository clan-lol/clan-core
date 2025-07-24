---
hide:
  - navigation
  - toc
---

# :material-home: What is Clan?

[Clan](https://clan.lol/) is a peer-to-peer computer management framework that
empowers you to reclaim control over your digital computing experience. Built on
NixOS, Clan provides a unified interface for managing networks of machines with
automated [secret management](./guides/secrets.md), secure [mesh VPN
connectivity](./guides/mesh-vpn.md), and customizable installation images. Whether
you're running a homelab or building decentralized computing infrastructure,
Clan simplifies configuration management while restoring your independence from
closed computing ecosystems.

At the heart of Clan are [Clan Services](./reference/clanServices/index.md) - the core
concept that enables you to add functionality across multiple machines in your
network. While Clan ships with essential core services, you can [create custom
services](./guides/clanServices.md) tailored to your specific needs.

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
