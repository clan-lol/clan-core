This guide will help you convert your existing NixOS configurations into a Clan.

!!! Warning
    Migrating instead of starting new can be trickier and might lead to bugs or
    unexpected issues. We recommend reading the [Getting Started](/guides/getting-started/creating-your-first-clan.md) guide first.

    Once you have a working setup and understand the concepts transfering your NixOS configurations over is easy.

## Back up your existing configuration

Before you start, it is strongly recommended to back up your existing
configuration in any form you see fit. If you use version control to manage
your configuration changes, it is also a good idea to follow the migration
guide in a separte branch until everything works as expected.

## Starting Point

We assume you are already using NixOS flakes to manage your configuration. If
not, migrate to a flake-based setup following the official [NixOS
documentation](https://nix.dev/manual/nix/2.25/command-ref/new-cli/nix3-flake.html).
The snippet below shows a common Nix flake. For this example we will assume you
have have two hosts: **berlin** and **cologne**.

```nix
{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs, ... }: {

    nixosConfigurations = {

      berlin = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [ ./machines/berlin/configuration.nix ];
      };

      cologne = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [ ./machines/cologne/configuration.nix ];
      };
    };
  };
}
```

## 1. Add `clan-core` to `inputs`

Add `clan-core` to your flake as input.

```nix
inputs.clan-core = {
  url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  # Don't do this if your machines are on nixpkgs stable.
  inputs.nixpkgs.follows = "nixpkgs";
}
```

## 2. Update Outputs

To be able to access our newly added dependency, it has to be added to the
output parameters.

```diff
-  outputs = { self, nixpkgs, ... }:
+  outputs = { self, nixpkgs, clan-core }:
```

The existing `nixosConfigurations` output of your flake will be created by
clan. In addition, a new `clanInternals` output will be added. Since both of
these are provided by the output of `clan-core.lib.clan`, a common syntax is to use a
`let...in` statement to create your clan and access it's parameters in the flake
outputs.

For the provide flake example, your flake should now look like this:

```nix
{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  inputs.clan-core = {
    url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, clan-core, ... }:
  let
    clan = clan-core.lib.clan {
      self = self; # this needs to point at the repository root
      specialArgs = {};
      meta.name = throw "Change me to something unique";

      machines = {
        berlin = {
          nixpkgs.hostPlatform = "x86_64-linux";
          imports = [ ./machines/berlin/configuration.nix ];
        };
        cologne = {
          nixpkgs.hostPlatform = "x86_64-linux";
          imports = [ ./machines/cologne/configuration.nix ];
        };
      };
    };
  in
  {
      inherit (clan.config) nixosConfigurations nixosModules clanInternals;
      clan = clan.config;
  };
}
```

✅ Et voilà! Your existing hosts are now part of a clan.

Existing Nix tooling
should still work as normal. To check that you didn't make any errors, run `nix
flake show` and verify both hosts are still recognized as if nothing had
changed. You should also see the new `clan` output.

```
❯ nix flake show
git+file:///my-nixos-config
├───clan: unknown
└───nixosConfigurations
    ├───berlin: NixOS configuration
    └───cologne: NixOS configuration
```

Of course you can also rebuild your configuration using `nixos-rebuild` and
veryify everything still works.

## 3. Add `clan-cli` to your `devShells`

At this point Clan is set up, but you can't use the CLI yet. To do so, it is
recommended to expose it via a `devShell` in your flake. It is also possible to
install it any other way you would install a package in Nix, but using a
developtment shell ensures the CLI's version will always be in sync with your
configuration.

A minimal example is provided below, add it to your flake outputs.

```nix
devShells."x86_64-linux".default = nixpkgs.legacyPackages."x86_64-linux".mkShell {
  packages = [ clan-core.packages."x86_64-linux".clan-cli ];
}
```

To use the CLI, execute `nix develop` in the directory of your flake. The
resulting shell, provides you with the `clan` CLI tool. Since you will be using
it every time you interact with Clan, it is recommended to set up
[direnv](https://direnv.net/).

Verify everything works as expected by running `clan machines list`.

```
❯ nix develop
[user@host:~/my-nixos-config]$ clan machines list
berlin
cologne
```

## Specify Targets

Clan needs to know where it can reach your hosts. For testing purpose set
`clan.core.networking.targetHost` to the machines adress or hostname.

```nix
# machines/berlin/configuration.nix
{
  clan.core.networking.targetHost = "123.4.56.78";
}
```

See our guide on for properly [configuring machines networking](../networking/networking.md)

## Next Steps

You are now fully set up. Use the CLI to manage your hosts or proceed to
configure further services. At this point you should be able to run commands
like `clan machines update berlin` to deploy a host.
