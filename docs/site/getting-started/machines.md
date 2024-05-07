# Deploy Machine

Integrating a new machine into your Clan environment is an easy yet flexible process, allowing for a straight forward management of multiple NixOS configurations.

We'll walk you through adding a new computer to your Clan.

## Installing a New Machine

Clan CLI, in conjunction with [nixos-anywhere](https://github.com/nix-community/nixos-anywhere), provides a seamless method for installing NixOS on various machines.

This process involves preparing a suitable hardware and disk partitioning configuration and ensuring the target machine is accessible via SSH.

### Step 0. Prerequisites

=== "**Physical Hardware**"

    - [x] **Two Computers**: You need one computer that you're getting ready (we'll call this the Target Computer) and another one to set it up from (we'll call this the Setup Computer). Make sure both can talk to each other over the network using SSH.
    - [x] **Machine configuration**: See our basic [configuration guide](./configure.md)
    - [x] **Initialized secrets**: See [secrets](secrets.md) for how to initialize your secrets.
    - [x] **USB Flash Drive**: See [Clan Installer](installer.md)

    !!! Steps
    
        1. Create a NixOS installer image and transfer it to a bootable USB drive as described in the [installer](./installer.md).
         
        2. Boot the target machine and connect it to a network that makes it reachable from your setup computer.

=== "**Baremetal Machines**"

    - [x] **Two Computers**: You need one computer that you're getting ready (we'll call this the Target Computer) and another one to set it up from (we'll call this the Setup Computer). Make sure both can talk to each other over the network using SSH.
    - [x] **Machine configuration**: See our basic [configuration guide](./configure.md)
    - [x] **Initialized secrets**: See [secrets](secrets.md) for how to initialize your secrets.

    !!! Steps

        - Any cloud machine if it is reachable via SSH and supports `kexec`.

Confirm the machine is reachable via SSH from your setup computer.

```bash
ssh root@<your_target_machine_ip>
```

### Step 1. Deploy the machine

**Finally deployment time!** Use the following command to build and deploy the image via SSH onto your machine.

=== "**SSH access**"



    Replace `<target_host>` with the **target computers' ip address**:

    ```bash
    clan machines install my-machine <target_host>
    ```

    !!!note 
        Building and deploying time will depend on hardware and connection speed.

=== "**Image Installer**"

    This method makes use of the image installers of [nixos-images](https://github.com/nix-community/nixos-images).
    See how to prepare the installer for use [here](./installer.md).

    The installer will randomly generate a password and local addresses on boot, then run ssh with these preconfigured.
    The installer shows it's deployment relevant information in two formats, a text form, as well as a QR code.

    ???example "An example view of a booted installer." 
        This is an example of the booted installer.

        ```{ .bash .annotate }
        ┌─────────────────────────────────────────────────────────────────────────────────────┐
        │ ┌───────────────────────────┐                                                       │
        │ │███████████████████████████│ # This is the QR Code (1)                             │
        │ │██ ▄▄▄▄▄ █▀▄█▀█▀▄█ ▄▄▄▄▄ ██│                                                       │
        │ │██ █   █ █▀▄▄▄█ ▀█ █   █ ██│                                                       │
        │ │██ █▄▄▄█ █▀▄ ▀▄▄▄█ █▄▄▄█ ██│                                                       │
        │ │██▄▄▄▄▄▄▄█▄▀ ▀▄▀▄█▄▄▄▄▄▄▄██│                                                       │
        │ │███▀▀▀ █▄▄█ ▀▄   ▄▀▄█   ███│                                                       │
        │ │██▄██▄▄█▄▄▀▀██▄▀ ▄▄▄ ▄▀█▀██│                                                       │
        │ │██ ▄▄▄▄▄ █▄▄▄▄ █ █▄█ █▀ ███│                                                       │
        │ │██ █   █ █ █  █ ▄▄▄  ▄▀▀ ██│                                                       │
        │ │██ █▄▄▄█ █ ▄ ▄    ▄ ▀█ ▄███│                                                       │
        │ │██▄▄▄▄▄▄▄█▄▄▄▄▄▄█▄▄▄▄▄█▄███│                                                       │
        │ │███████████████████████████│                                                       │
        │ └───────────────────────────┘                                                       │
        │ ┌─────────────────────────────────────────────────────────────────────────────────┐ │
        │ │Root password: cheesy-capital-unwell  # password (2)                             │ │
        │ │Local network addresses:                                                         │ │
        │ │enp1s0           UP    192.168.178.169/24 metric 1024 fe80::21e:6ff:fe45:3c92/64 │ │
        │ │enp2s0           DOWN                                                            │ │
        │ │wlan0            DOWN # connect to wlan (3)                                      │ │
        │ │Onion address: 6evxy5yhzytwpnhc2vpscrbti3iktxdhpnf6yim6bbs25p4v6beemzyd.onion    │ │
        │ │Multicast DNS: nixos-installer.local                                             │ │
        │ └─────────────────────────────────────────────────────────────────────────────────┘ │
        │ Press 'Ctrl-C' for console access                                                   │ 
        │                                                                                     │
        └─────────────────────────────────────────────────────────────────────────────────────┘
        ```
 
        1.  This is not an actual QR code, because it is displayed rather poorly on text sites.
            This would be the actual content of this specific QR code prettified:
            ```json
            {
              "pass": "cheesy-capital-unwell",
              "tor": "6evxy5yhzytwpnhc2vpscrbti3iktxdhpnf6yim6bbs25p4v6beemzyd.onion",
              "addrs": [
                "2001:9e8:347:ca00:21e:6ff:fe45:3c92"
              ]
            }
            ```
            
            To generate the actual QR code, that would be displayed use:
            ```shellSession
            echo '{"pass":"cheesy-capital-unwell","tor":"6evxy5yhzytwpnhc2vpscrbti3iktxdhpnf6yim6bbs25p4v6beemzyd.onion","addrs":["2001:9e8:347:ca00:21e:6ff:fe45:3c92"]}' | nix run nixpkgs#qrencode -- -s 2 -m 2 -t utf8
            ```
        2.  The root password for the installer medium.
            This password is autogenerated and meant to be easily typeable.
        3.  See how to connect the installer medium to wlan [here](./installer.md#optional-connect-to-wifi).
        4.  :man_raising_hand: I'm a code annotation! I can contain `code`, __formatted
            text__, images, ... basically anything that can be written in Markdown.

    
    !!!tip
        We recommend using KDE Connect for sharing the deployment information from the QR code with the deploying machine.

    
    The QR code can be used to deploy either with an image, that is decoded on the fly, or it's contained json information.

    With the path to a `json` string, or the string itself:
    ```terminal
    clan machines install [MACHINE] --json [JSON]
    ```
    With the path to an image containing the relevant QR code:
    ```terminal
    clan machines install [MACHINE] --png [PATH]
    ```


!!! success

    Your machine is all set up. 🎉 🚀

---

## What's next ?

- [**Update a Machine**](#update-your-machines): Learn how to update an existing machine?
- [**Configure a Private Network**](./networking.md): Configuring a secure mesh network.

---

## Update Your Machines

Clan CLI enables you to remotely update your machines over SSH. This requires setting up a target address for each target machine.

### Setting the Target Host

Replace `host_or_ip` with the actual hostname or IP address of your target machine:

```bash
clan config --machine my-machine clan.networking.targetHost root@host_or_ip
```

!!! warning
    The use of `root@` in the target address implies SSH access as the `root` user.
    Ensure that the root login is secured and only used when necessary.

### Updating Machine Configurations

Execute the following command to update the specified machine:

```bash
clan machines update my-machine
```

You can also update all configured machines simultaneously by omitting the machine name:

```bash
clan machines update
```

### Setting a Build Host

If the machine does not have enough resources to run the NixOS evaluation or build itself,
it is also possible to specify a build host instead.
During an update, the cli will ssh into the build host and run `nixos-rebuild` from there.

```bash
clan config --machine my-machine clan.networking.buildHost root@host_or_ip
```

### Excluding a machine from `clan machine update`

To exclude machines from being updated when running `clan machines update` without any machines specified,
one can set the `clan.deployment.requireExplicitUpdate` option to true:

```bash
clan config --machine my-machine clan.deployment.requireExplicitUpdate true
```

This is useful for machines that are not always online or are not part of the regular update cycle.

---

# TODO:
* TODO: How to join others people zerotier
  * `services.zerotier.joinNetworks = [ "network-id" ]`
* Controller needs to approve over webinterface or cli
