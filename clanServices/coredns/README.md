!!! Danger "Experimental"
    This service is experimental and will change in the future.

This module enables hosting clan-internal services easily, which can be resolved
inside your VPN. This allows defining a custom top-level domain (e.g. `.clan`)
and exposing endpoints from a machine to others, which will be
accessible under `http://<service>.clan` in your browser.

The service consists of two roles:

- A `server` role: This is the DNS-server that will be queried when trying to
  resolve clan-internal services. It defines the top-level domain.
- A `default` role: This does two things. First, it sets up the nameservers so
  that clan-internal queries are resolved via the `server` machine, while
  external queries are resolved as normal via DHCP. Second, it allows exposing
  services (see example below).

## Example Usage

Here the machine `dnsserver` is designated as internal DNS-server for the TLD
`.foo`. `server01` will host an application that shall be reachable at
`http://one.foo` and `server02` is going to be reachable at `http://two.foo`.
`client` is any other machine that is part of the clan but does not host any
services.

When `client` tries to resolve `http://one.foo`, the DNS query will be
routed to `dnsserver`, which will answer with `192.168.1.3`. If it tries to
resolve some external domain (e.g. `https://clan.lol`), the query will not be
routed to `dnsserver` but resolved as before, via the nameservers advertised by
DHCP.

```nix
inventory = {

  machines = {
    dnsserver = { }; # 192.168.1.2
    server01 = { };  # 192.168.1.3
    server02 = { };  # 192.168.1.4
    client = { };    # 192.168.1.5
  };

  instances = {
    coredns = {

      module.name = "@clan/coredns";
      module.input = "self";

      # Add the default role to all machines, including `client`
      roles.default.tags.all = { };

      # DNS server queries to http://<name>.foo are resolved here
      roles.server.machines."dnsserver".settings = {
        ip = "192.168.1.2";
        tld = "foo";
      };

      # First service
      # Registers http://one.foo will resolve to 192.168.1.3
      # underlying service runs on server01
      roles.default.machines."server01".settings = {
        ip = "192.168.1.3";
        services = [ "one" ];
      };

      # Second service
      roles.default.machines."server02".settings = {
        ip = "192.168.1.4";
        services = [ "two" ];
      };
    };
  };
};
```
