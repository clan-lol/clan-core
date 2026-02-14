Services provided by the community, with no stability guarantees! 

<div class="grid cards" markdown>

-  [desktop](https://git.clan.lol/clan/clan-community/src/branch/main/services/desktop) :octicons-link-external-16:

    ---

    Allows setting up [KDE](https://kde.org) or [Sway](https://swaywm.org/) via
    roles. The service will also set up a display manager or greeter as needed
    and allows using multiple desktop environments or compositors at once.


-  [localsend](https://git.clan.lol/clan/clan-community/src/branch/main/services/localsend) :octicons-link-external-16:

    ---

    Sets up [localsend](https://localsend.org), an application to share files to nearby devices.


-  [wireguard-star](https://git.clan.lol/clan/clan-community/src/branch/main/services/wireguard-star) :octicons-link-external-16:

    ---

    Set up [WireGuard](https://wireguard.com) in a star topology. All machines
    with the peer role will connect to the controller. IPv4 addresses are
    manually assigned. For an IPv6 service that also supports multiple
    controllers in a mesh topology, see the official
    [clan WireGuard service](https://docs.clan.lol/services/official/wireguard/)


- [Nix Cache](https://github.com/DavHau/hyperconfig/tree/master/modules/clan/nix-cache) :octicons-link-external-16:

    ---

    Sets up a nix cache to share the nix store between machines in your network 


- [@schallerclan/dns](https://git.clan.lol/dafitt/schallerclan/src/branch/main/clanServices/dns.nix) :octicons-link-external-16:

    ---

    Clan-internal DNS and service exposure with support for multiple records (e.g. A, AAAA, CNAME) and multiple IPs

- [@schallerclan/tailscale](https://git.clan.lol/dafitt/schallerclan/src/branch/main/clanServices/tailscale.nix) :octicons-link-external-16:

    ---

    Connect to a tailscale network. Very basic tailscale support.

</div>

## clan-community repository

Looking for more community-maintained services and modules? Check out the
[clan-community](https://git.clan.lol/clan/clan-community) repository — a
shared collection of services maintained by the clan community.

!!! tip "Add your own!"

    Have you built a service or a tool? Open a PR adding a link to this page, or
    contribute directly to
    [clan-community](https://git.clan.lol/clan/clan-community)!
