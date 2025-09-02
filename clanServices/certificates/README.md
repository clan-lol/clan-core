This service sets up a certificate authority (CA) that can issue certificates to
other machines in your clan. For this the `ca` role is used.
It additionally provides a `default` role, that can be applied to all machines
in your clan and will make sure they trust your CA.

## Example Usage

The following configuration would add a CA for the top level domain `.foo`. If
the machine `server` now hosts a webservice at `https://something.foo`, it will
get a certificate from `ca` which is valid inside your clan. The machine
`client` will trust this certificate if it makes a request to
`https://something.foo`.

This clan service can be combined with the `coredns` service for easy to deploy,
SSL secured clan-internal service hosting.

```nix
inventory = {
  machines.ca = { };
  machines.client = { };
  machines.server = { };

  instances."certificates" = {
    module.name = "certificates";
    module.input = "self";

    roles.ca.machines.ca.settings.tlds = [ "foo" ];
    roles.default.machines.client = { };
    roles.default.machines.server = { };
  };
};
```
