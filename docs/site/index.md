---
hide:
  - toc
---

# What is Clan?
<style>
  .clamp-wrap {
    --lines: 5;           /* visible lines when collapsed */
    --fade-height: 2.5rem;/* fade size */
    font: inherit;
    color: inherit;
    position: relative;
  }

  /* Accessible, visually hidden checkbox */
  .clamp-toggle {
    position: absolute;
    width: 1px; height: 1px;
    margin: -1px; border: 0; padding: 0;
    clip: rect(0 0 0 0); clip-path: inset(50%);
    overflow: hidden; white-space: nowrap;
  }

  .clamp-content {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: var(--lines);
    overflow: hidden;

    /* Fade via mask (no overlay needed) */
    -webkit-mask-image: linear-gradient(
      to bottom,
      black,
      black calc(100% - var(--fade-height)),
      transparent
    );
    mask-image: linear-gradient(
      to bottom,
      black,
      black calc(100% - var(--fade-height)),
      transparent
    );
  }

  /* Right-aligned Read more/less */
  .clamp-more {
    display: block;
    width: max-content;
   /* margin-left: auto; */
    margin-top: 0.5rem;
    cursor: pointer;
    color: #0057d9;
    text-decoration: underline;
    user-select: none;
  }
  .clamp-more:hover,
  .clamp-more:focus { text-decoration: none; }

  /* Expanded state */
  .clamp-toggle:checked ~ .clamp-content {
    -webkit-line-clamp: initial;
    display: block;
    -webkit-mask-image: none;
    mask-image: none;
  }

  /* Dynamic label text */
  .clamp-more::after { content: "Read more"; }
  .clamp-toggle:checked ~ .clamp-more::after { content: "Read less"; }
</style>

<div class="clamp-wrap" style="--lines: 3;">
  <input type="checkbox" id="clan-readmore" class="clamp-toggle" />
  <div class="clamp-content">
    <p><a href="https://clan.lol/">Clan</a> is a peer-to-peer computer management framework that empowers you to selfhost in a reliable and scalable way</strong>.</p>
    <p>Built on NixOS, Clan provides a declarative interface for managing machines</strong> with automated <a href="./guides/secrets.md">secret management</a>, easy <a href="./guides/mesh-vpn.md">mesh VPN connectivity</a>, and <a href="./guides/backups.md">automated backups</a>.</p>
    <p>Whether you're running a homelab or maintaining critical computing infrastructure, Clan will help reduce maintenance burden</strong> by allowing a git repository to define your whole network</strong> of computers.</p>
    <p>In combination with <a href="https://github.com/Mic92/sops-nix">sops-nix</a>, <a href="https://github.com/nix-community/nixos-anywhere">nixos-anywhere</a> and <a href="https://github.com/nix-community/disko">disko</a>, Clan makes it possible to have collaborative infrastructure</strong>.</p>
    <p>At the heart of Clan are <a href="./reference/clanServices/index.md">Clan Services</a> - the core concept that enables you to add functionality across multiple machines in your network. While Clan ships with essential core services, you can <a href="./guides/inventory/clanServices.md">create custom services</a> tailored to your specific needs.</p>
  </div>
  <label class="clamp-more" for="clan-readmore"></label>
</div>

---

[Get started](./guides/getting-started/index.md){ .md-button .md-button--primary }
[View on Gitea](https://git.clan.lol/clan/clan-core){ .md-button }

## Guides

<div class="grid cards" markdown>

-   [Inventory](./guides/inventory/inventory.md)

    ---

    Learn how about inventory

-   [Vars](./guides/vars/vars-overview.md)

    ---

    Learn how to use vars

-   [macOS](./guides/macos.md)

    ---

    Using Clan to manage your macOS machines

</div>

## Reference

<div class="grid cards" markdown>

-   [CLI](./reference/cli/index.md)

    ---

    command line interface

-   [Clan Options](/options)

    ---

    Search all options

-   [Services](./reference/clanServices/index.md)

    ---

    Discover services

</div>

## Blog

<div class="grid cards" markdown>

-   [Clan Blog](https://clan.lol/blog/)

    ---

    For the latest updates, tutorials, and community stories.

</div>
