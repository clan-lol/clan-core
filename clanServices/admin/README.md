The admin service aggregates components that allow an administrator to log in to and manage the machine.

The following configuration:

1. Enables OpenSSH with root login and adds an SSH public key named`myusersKey` to the machine's authorized_keys via the `allowedKeys` setting.

2. Automatically generates a password for the root user.

```nix
instances = {
    admin = {
        roles.default.tags = {
            all = {  };
        };
        roles.default.settings = {
            allowedKeys = {
                myusersKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEFDNnynMbFWatSFdANzbJ8iiEKL7+9ZpDaMLrWRQjyH lhebendanz@wintux";
            };
        };
    };
};
```



