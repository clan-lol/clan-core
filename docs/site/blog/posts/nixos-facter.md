---
title: "Introducing NixOS Facter"
description: "Declarative Hardware Configuration in NixOS"
authors:
  - BrianMcGee
date: 2024-07-19
slug: nixos-facter
---

If you've ever installed [NixOS], you'll be familiar with a little Perl script called [nixos-generate-config]. Unsurprisingly, it generates a couple of NixOS modules based on available hardware, mounted filesystems, configured swap, etc.

It's a critical component of the install process, aiming to ensure you have a good starting point for your NixOS system, with necessary or recommended kernel modules, file system mounts, networking config and much more.

As solutions go, it's a solid one. It has helped many users take their first steps into this rabbit hole we call NixOS. However, it does suffer from one fundamental limitation.

## Static Generation

When a user generates a `hardware-configuration.nix` with `nixos-generate-config`, it makes choices based on the current state of the world as it sees it. By its very nature, then, it cannot account for changes in NixOS over time.

A recommended configuration option today might be different two NixOS releases from now.

To account for this, you could always run `nixos-generate-config` again. But that requires a working system, which may have broken due to the historical choices made last time, or worst-case, requiring you to fire up the installer again.

## A Layer of Indirection

What if, instead of generating some Nix code, we first describe the current hardware in an intermediate format? This hardware report would be _'pure'_, devoid of any reference to NixOS, and intended as a stable, longer-term representation of the system.

From here, we can create a series of NixOS modules designed to examine the report's contents and make the same kinds of decisions that `nixos-generate-config` does. The critical difference is that as NixOS evolves, so can these modules, and with a full hardware report available we can make more interesting config choices about things such as GPUs and other devices.

In a perfect world, we should not need to regenerate the underlying report as long as there are no hardware changes. We can take this one step further.

Provided that certain sensitive information, such as serial numbers and MAC addresses, is filtered out, there is no reason why these hardware reports could not be shared after they are generated for things like EC2 instance types, specific laptop models, and so on, much like [NixOS Hardware] currently shares Nix configs.

## Introducing NixOS Facter

Still in its early stages, [NixOS Facter] is intended to do what I've described above.

A user can generate a JSON-based hardware report using a (eventually static) Go program: `nixos-facter -o facter.json`. From there, they can include this report in their NixOS config and make use of our [NixOS modules](https://github.com/numtide/nixos-facter-modules) as follows:

=== "**flake.nix**"

    ```nix
    {
        inputs = {
            nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
            nixos-facter-modules.url = "github:numtide/nixos-facter-modules";
        };

        outputs = inputs @ {
            nixpkgs,
            ...
        }: {
            nixosConfigurations.basic = nixpkgs.lib.nixosSystem {
                modules = [
                    inputs.nixos-facter-modules.nixosModules.facter
                    { config.facter.reportPath = ./facter.json; }
                    # ...
                ];
            };
        };
    }
    ```

=== "**without flakes**"

    ```nix
    # configuration.nix
    {
        imports = [
          "${(builtins.fetchTarball {
            url = "https://github.com/numtide/nixos-facter-modules/";
          })}/modules/nixos/facter.nix"
        ];

        config.facter.reportPath = ./facter.json;
    }
    ```

That's it.

> We assume that users will rely on [disko], so we have not implemented file system configuration yet (it's on the roadmap). 
> In the meantime, if you don't use disko you have to specify that part of the configuration yourself or take it from `nixos-generate-config`.


## Early Days

Please be aware that [NixOS Facter] is still in early development and is still subject to significant changes especially the output json format as we flesh things out. Our initial goal is to reach feature parity with [nixos-generate-config].

From there, we want to continue building our NixOS modules, opening things up to the community, and beginning to capture shared hardware configurations for providers such as Hetzner, etc.

Over the coming weeks, we will also build up documentation and examples to make it easier to play with. For now, please be patient.

> Side note: if you are wondering why the repo is in the [Numtide] org, we started partnering with Clan! Both companies are looking to make self-hosting easier and we're excited to be working together on this. Expect more tools and features to come!

[NixOS Facter]: https://github.com/numtide/nixos-facter
[NixOS Hardware]: https://github.com/NixOS/nixos-hardware
[NixOS]: https://nixos.org "Declarative builds and deployments"
[Numtide]: https://numtide.com
[disko]: https://github.com/nix-community/disko
[nixos-generate-config]: https://github.com/NixOS/nixpkgs/blob/dac9cdf8c930c0af98a63cbfe8005546ba0125fb/nixos/modules/installer/tools/nixos-generate-config.pl
