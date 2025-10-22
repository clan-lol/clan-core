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

```nix {.nix title="flake.nix" hl_lines="19-25"}
{
  inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  inputs.nixpkgs.follows = "clan-core/nixpkgs";

  outputs =
    { self, clan-core, ... }:
    let
      # Sometimes this attribute set is defined in clan.nix
      clan = clan-core.lib.clan {
        inherit self;

        meta.name = "myclan";
        meta.tld = "ccc";

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

Update the `controller` machine first:

```bash
clan machines update controller
```

Then update all other peers:

```bash
clan machines update
```

### Verify Connection

On the `new_machine` run:

```bash
$ sudo zerotier-cli info
```

The status should be "ONLINE":

```{.console, .no-copy}
200 info d2c71971db 1.12.1 ONLINE
```

## Further
Currently **Zerotier** is the only mesh-vpn that is fully integrated into clan.
In the future we plan to add additional network technologies like tinc, head/tailscale
Currently we support yggdrassil and mycelium through usage of the inventory, 
though it is not yet integrated into the networking module.

We chose ZeroTier because in our tests it was a straight forward solution to bootstrap.
It allows you to selfhost a controller and the controller doesn't need to be globally reachable.
Which made it a good fit for starting the project.

## Debugging

### Retrieve the ZeroTier ID

In the repo:

```console
$ clan vars list <machineName>
```

```{.console, .no-copy}
$ clan vars list controller
# ... elided
zerotier/zerotier-identity-secret: ********
zerotier/zerotier-ip: fd0a:b849:2928:1234:c99:930a:a959:2928
zerotier/zerotier-network-id: 0aa959282834000c
```

On the machine:

```bash
$ sudo zerotier-cli info
```

#### Manually Authorize a Machine on the Controller

=== "with ZeroTierIP"

      ```bash
      $ sudo zerotier-members allow --member-ip <IP>
      ```

      Substitute `<IP>` with the ZeroTier IP obtained previously.

=== "with ZeroTierID"

      ```bash
      $ sudo zerotier-members allow <ID>
      ```

      Substitute `<ID>` with the ZeroTier ID obtained previously.
