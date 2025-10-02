This module allows you to pre-configure WiFi networks for automatic connection.  
Each attribute in `settings.network` serves as an internal identifier, not the actual SSID.  
After defining your networks, you will be prompted for the SSID and password for each one.

This module leverages NetworkManager for managing connections.

```nix
instances = {
    wifi = {
        module.name = "wifi";
        module.input = "clan-core";

        roles.default = {
            machines."jon" = {
                settings.networks.home = { };
                settings.networks.work = { keyMgmt = "wpa-eap"; };
            };
        };
    };
};
```
