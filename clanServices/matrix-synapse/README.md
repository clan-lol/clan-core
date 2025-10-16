This NixOS module installs and configures Synapse — a federated Matrix homeserver with end-to-end encryption — and optionally provides the Element web client.

The example below demonstrates a minimal setup that includes:

- Element web client.
- Synapse backed by PostgreSQL and nginx.
- An admin user and an additional regular user.

Example configuration:

```nix
instances = {
    matrix-synapse = {
        roles.default.machines."jon".settings = {
            acmeEmail = "admins@clan.lol";
            server_tld = "clan.test";
            app_domain = "matrix.clan.test";
            users.admin.admin = true;
            users.someuser = { };
        };
    };
};
```