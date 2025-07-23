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

-   [Adding more machines](./guides/more-machines.md)

    ---

    Learn how Clan automatically includes machines and Nix files.

-   [Vars Backend](./guides/vars-backend.md)

    ---

    Learn how to manage secrets with vars.

-   [Inventory](./guides/inventory.md)

    ---

    Clan's declaration format for running **services** on one or multiple **machines**.

-   [Flake-parts](./guides/flake-parts.md)

    ---

    Use Clan with [https://flake.parts/]()

-   [Contribute](./developer/contributing/CONTRIBUTING.md)

    ---

    Discover how to set up a development environment to contribute to Clan!

-   [macOS machines](./guides/macos.md)

    ---

    Manage macOS machines with nix-darwin

</div>

## API Reference

**Reference API Documentation**

<div class="grid cards" markdown>

-   [CLI Reference](./reference/cli/index.md)

    ---

    The `clan` CLI command

-   [Service Modules](./reference/clanServices/index.md)

    ---

    An overview of available service modules

-   [Core](./reference/clan.core/index.md)

    ---

    The clan core nix module.
    This is imported when using clan and is the basis of the extra functionality
    that can be provided.

-   [(Legacy) Modules](./reference/clanModules/index.md)

    ---

    An overview of available clanModules

    !!! Example "These will be deprecated soon"


</div>
