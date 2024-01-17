# ZeroTier Configuration with NixOS in Clan

This guide provides detailed instructions for configuring
[ZeroTier VPN](https://zerotier.com) within Clan. Follow the
outlined steps to set up a machine as a VPN controller (`<CONTROLLER>`) and to
include a new machine into the VPN.

## 1. Setting Up the VPN Controller

The VPN controller is initially essential for providing configuration to new
peers. Post the address allocation, the controller's continuous operation is not
crucial.

### Instructions:

1. **Designate a Machine**: Label a machine as the VPN controller in the clan,
   referred to as `<CONTROLLER>` henceforth in this guide.
2. **Add Configuration**: Input the below configuration to the NixOS
   configuration of the controller machine:
   ```nix
   clan.networking.zerotier.controller = {
     enable = true;
     public = true;
   };
   ```
3. **Update the Controller Machine**: Execute the following:
   ```console
   $ clan machines update <CONTROLLER>
   ```
   Your machine is now operational as the VPN controller.

## 2. Integrating a New Machine to the VPN

To introduce a new machine to the VPN, adhere to the following steps:

### Instructions:

1. **Update Configuration**: On the new machine, incorporate the below to its
   configuration, substituting `<CONTROLLER>` with the controller machine name:
   ```nix
   { config, ... }: {
     clan.networking.zerotier.networkId = builtins.readFile (config.clanCore.clanDir + "/machines/<CONTROLLER>/facts/zerotier-network-id");
   }
   ```
2. **Update the New Machine**: Execute:
   ```console
   $ clan machines update <NEW_MACHINE>
   ```
   Replace `<NEW_MACHINE>` with the designated new machine name.
3. **Retrieve the ZeroTier ID**: On the `new_machine`, execute:
   ```console
   $ sudo zerotier-cli info
   ```
   Example Output: `200 info d2c71971db 1.12.1 OFFLINE`, where `d2c71971db` is
   the ZeroTier ID.
4. **Authorize the New Machine on Controller**: On the controller machine,
   execute:
   ```console
   $ sudo zerotier-members allow <ID>
   ```
   Substitute `<ID>` with the ZeroTier ID obtained previously.
5. **Verify Connection**: On the `new_machine`, re-execute:
   ```console
   $ sudo zerotier-cli info
   ```
   The status should now be "ONLINE" e.g., `200 info 47303517ef 1.12.1 ONLINE`.

Congratulations! The new machine is now part of the VPN, and the ZeroTier
configuration on NixOS within the Clan project is complete.
