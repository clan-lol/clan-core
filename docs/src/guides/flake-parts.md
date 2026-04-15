# Flake Parts

[flake-parts](https://flake.parts/) is a framework for composing Nix flakes out of small, reusable modules. This guide shows you how to set up Clan inside a flake-parts project, so you can define your machines with Clan's options alongside whatever other flake-parts modules you already use.

The setup is three steps: add the inputs, import Clan's flake-parts module, and define your clan and machines.

## 1. Add the inputs

Add `flake-parts` to your `flake.nix` and wire it together with `clan-core`:

```nix [flake.nix]
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs?ref=nixos-unstable";

  flake-parts.url = "github:hercules-ci/flake-parts";
  flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";

  clan-core = {
    url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
    inputs.nixpkgs.follows = "nixpkgs";
    inputs.flake-parts.follows = "flake-parts";
  };
};
```

The two `follows` lines on `clan-core` tell it to reuse your `nixpkgs` and `flake-parts` instead of bringing in its own copies. Without them you end up with duplicate inputs in `flake.lock`. See [Nixpkgs Flake Input](/docs/guides/nixpkgs-flake-input) for how to diagnose and clean that up.

:::admonition[Note]{type=note}
If you want to track the exact `nixpkgs` that Clan's CI tests against, use `nixpkgs.follows = "clan-core/nixpkgs"` instead. The [Nixpkgs Flake Input guide](/docs/guides/nixpkgs-flake-input) explains the trade-off.
:::

## 2. Import the Clan flake-parts module

Inside `mkFlake`, import Clan's module so its [options](/docs/reference/options/clan) become available:

```nix
{
  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.clan-core.flakeModules.default
      ];
    };
}
```

This pulls the `clan` option into your flake-parts configuration. Everything in the next step goes under that option.

## 3. Configure your clan and machines

Fill in your clan metadata and define at least one machine:

```nix [flake.nix]
{
  outputs =
    inputs@{ flake-parts, clan-core, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
      ];

      imports = [
        clan-core.flakeModules.default
      ];

      clan = {
        meta.name = "my-clan";
        meta.domain = "my-clan.lol";

        machines = {
          jon = {
            imports = [
              ./modules/firefox.nix
            ];

            nixpkgs.hostPlatform = "x86_64-linux";

            clan.core.networking.targetHost = "root@jon";

            disko.devices.disk.main = {
              device = "/dev/disk/by-id/nvme-eui.e8238fa6bf530001001b448b4aec2929";
            };
          };
        };
      };
    };
}
```

A few things are happening here:

- `systems` is a flake-parts option. It lists the host platforms that `perSystem` outputs are built for. Add `"aarch64-linux"` or a Darwin system if you need them.
- `clan.meta.name` and `clan.meta.domain` identify your clan. Both are required and both must be unique across the clans you manage.
- Each entry under `clan.machines` is a NixOS configuration. `imports` pulls in your own NixOS modules, `nixpkgs.hostPlatform` sets the target architecture, and `clan.core.networking.targetHost` is the SSH destination Clan uses when you run `clan machines update jon` or `clan ssh jon`.
- `disko.devices.disk.main.device` points at the disk that NixOS will be installed onto. Use a stable `/dev/disk/by-id/...` path so it does not change between boots.

For the full list of options the Clan flake-parts module exposes, see the [module source](https://git.clan.lol/clan/clan-core/src/branch/main/flakeModules/clan.nix).
