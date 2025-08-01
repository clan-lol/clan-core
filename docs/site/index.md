---
hide:
  - navigation
  - toc
---

# :material-home: What is Clan?

[Clan](https://clan.lol/) is a peer-to-peer computer management framework that
empowers you to **selfhost in a reliable and scalable way**.

Built on NixOS, Clan provides a **declarative interface for managing machines** with automated [secret management](./guides/secrets.md), easy [mesh VPN
connectivity](./guides/mesh-vpn.md), and [automated backups](./guides/backups.md).

Whether you're running a homelab or maintaining critical computing infrastructure,
Clan will help **reduce maintenance burden** by allowing a **git repository to define your whole network** of computers.

In combination with [sops-nix](https://github.com/Mic92/sops-nix), [nixos-anywhere](https://github.com/nix-community/nixos-anywhere) and [disko](https://github.com/nix-community/disko), Clan makes it possible to have **collaborative infrastructure**.

At the heart of Clan are [Clan Services](./reference/clanServices/index.md) - the core
concept that enables you to add functionality across multiple machines in your
network. While Clan ships with essential core services, you can [create custom
services](./guides/clanServices.md) tailored to your specific needs.


## :material-book: Guides

How-to Guides for achieving a certain goal or solving a specific issue.

<div class="grid cards" markdown>

-   [:material-clock-fast: Getting Started](./guides/getting-started/index.md)

    ---

    Get started in less than 20 minutes!

-   [macOS](./guides/macos.md)

    ---

    Using Clan to manage your macOS machines

-   [Contribute](./guides/contributing/CONTRIBUTING.md)

    ---

    How to set up a development environment

</div>

## Concepts

Explore the underlying principles of Clan

<div class="grid cards" markdown>

-   [Generators](./concepts/generators.md)

    ---

    Learn about Generators, our way to secret management

-   [Inventory](./concepts/inventory.md)

    ---

    Learn about the Inventory, a multi machine Nix interface

</div>


## Blog

Visit our [Clan Blog](https://clan.lol/blog/) for the latest updates, tutorials, and community stories.
