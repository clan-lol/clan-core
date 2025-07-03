
This guide provides detailed instructions for configuring
[ZeroTier VPN](https://zerotier.com) within Clan. Follow the
outlined steps to set up a machine as a VPN controller (`<CONTROLLER>`) and to
include a new machine into the VPN.

## Concept

By default all machines within one clan are connected via a chosen network technology.

```{.no-copy}
Clan
    Node A
    <-> (zerotier / mycelium / ...)
    Node B
```

This guide shows you how to configure `zerotier` through clan's `Inventory` System.

## The Controller

The controller is the initial entrypoint for new machines into the vpn.
It will sign the id's of new machines.
Once id's are signed, the controller's continuous operation is not essential.
A good controller choice is nevertheless a machine that can always be reached for updates - so that new peers can be added to the network.

For the purpose of this guide we have two machines:

- The `controller` machine, which will be the zerotier controller.
- The `new_machine` machine, which is the machine we want to add to the vpn network.

## Configure the Service

Note: consider picking a more descriptive name for the VPN than "default".
It will be added as an altname for the Zerotier virtual ethernet interface, and
will also be visible in the Zerotier app.

```nix {.nix title="flake.nix" hl_lines="13-15"}
{
  inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  inputs.nixpkgs.follows = "clan-core/nixpkgs";

  outputs =
    { self, clan-core, ... }:
    let
      clan = clan-core.lib.clan {
        inherit self;

        meta.name = "myclan";

        inventory.machines = {
          controller = {};
          new_machine = {};
        };

        inventory.instances = {
          zerotier = {
            # Assign the controller machine to the role "controller"
            roles.controller.machines."controller" = {};

            # All clan machines are zerotier peers
            roles.peer.tags."all" = {};
          };
        };
      };
    in
    {
      inherit (clan) nixosConfigurations nixosModules clanInternals;

      # elided for brevity
    };
}
```

## Apply the Configuration
Update the `controller` machine:

```bash
clan machines update controller
```

## Further

Currently you can only use **Zerotier** as networking technology because this is the first network stack we aim to support.
In the future we plan to add additional network technologies like tinc, head/tailscale, yggdrassil and mycelium.

We chose zerotier because in our tests it was a straight forwards solution to bootstrap.
It allows you to selfhost a controller and the controller doesn't need to be globally reachable.
Which made it a good fit for starting the project.
