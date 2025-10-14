Services provided by the community, with no stability guarantees! 

<div class="grid cards" markdown>

-  [Desktop Service](https://github.com/pinpox/nixos/tree/3a50bf20d0f6897d5619087f83a0fe6a4118f806/clan-service-modules/desktop) :octicons-link-external-16:

    ---

    Allows setting up [KDE](https://kde.org) or [Sway](https://swaywm.org/) via
    roles. The service will also set up a display manager or greeter as needed
    and allows using multiple desktop environments or compositors at once.


-  [Localsend](https://github.com/pinpox/nixos/blob/3a50bf20d0f6897d5619087f83a0fe6a4118f806/clan-service-modules/localsend.nix) :octicons-link-external-16:

    ---

    Sets up [localsend](https://localsend.org), an application to share files to nearby devices.


-  [Wireguard Star](https://github.com/pinpox/nixos/blob/3a50bf20d0f6897d5619087f83a0fe6a4118f806/clan-service-modules/wireguard.nix) :octicons-link-external-16:

    ---

    Set up [wireguard](https://wireguard.com) in a star topology. All machines
    with the peer role will connect to the controller. IPv4 addresses are
    manually assigned. For a IPv6 service that also supports multiple
    controllers in a mesh topology, see the official
    [clan wireguard service](https://docs.clan.lol/services/official/wireguard/)

-  [Vaultwarden](https://github.com/Qubasa/infra/blob/main/modules/vaultwarden)
  
    ---

    Sets up the centralized open source password manager backend [vaultwarden](https://github.com/dani-garcia/vaultwarden) for [bitwarden](https://bitwarden.com/de-de/). 


-  [Easytier Mesh VPN](https://github.com/DavHau/hyperconfig/tree/master/modules/clan/easytier)

    ---

    Sets up the [EasyTier Mesh VPN](https://github.com/EasyTier/EasyTier), uses WirGuard under the hood.


- [Nix Cache](https://github.com/DavHau/hyperconfig/tree/master/modules/clan/nix-cache)

    ---

    Sets up a nix cache to share the nix store between machines in your network 



</div>

!!! tip "Add your own!"

    Have you built a service or a tool for? Open a PR adding a link to this page!
