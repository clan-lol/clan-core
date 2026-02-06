# Migrating from `admin` clanService to `sshd` and `users`

The `admin` clanService is deprecated. Its functionality has been split into dedicated services:

- **sshd** (server role): SSH authorized keys, host certificates, RSA host key generation
- **users**: Root password management

## Option Mappings

| Admin Option | New Service | New Option |
|-------------|-------------|------------|
| `allowedKeys` | sshd (server) | `authorizedKeys` |
| `certificateSearchDomains` | sshd (server) | `certificate.searchDomains` |
| `rsaHostKey.enable` | sshd (server) | `hostKeys.rsa.enable` |
| (root password) | users | `user = "root"` |

## Migration Steps

### Step 1: Replace admin with sshd

**Before** (admin service):

```nix
instances = {
  admin = {
    roles.default.tags.all = { };
    roles.default.settings = {
      allowedKeys = {
        "my-key" = "ssh-ed25519 AAAA...";
      };
      certificateSearchDomains = [ "mydomain.com" ];
      rsaHostKey.enable = true;
    };
  };
};
```

**After** (sshd service):

```nix
instances = {
  sshd = {
    roles.server.tags.all = { };
    roles.server.settings = {
      authorizedKeys = {
        "my-key" = "ssh-ed25519 AAAA...";
      };
      certificate.searchDomains = [ "mydomain.com" ];
      hostKeys.rsa.enable = true;
    };
    # Optional: add client role if you want machines to trust the CA
    roles.client.tags.all = { };
  };
};
```

### Step 2: Add root password via users service (if needed)

If you relied on the admin service's root password generation, add the users service:

```nix
instances = {
  root-user = {
    module = {
      name = "users";
      input = "clan-core";
    };
    roles.default.tags.all = { };
    roles.default.settings = {
      user = "root";
      prompt = true;  # Set to false to auto-generate password
    };
  };
};
```

## Vars Migration

The admin service generated vars with different names than the new services. After migration, you'll need to regenerate these vars:

| Admin var path | New service var path |
|----------------|----------------------|
| `root-password/password-hash` | `user-password-root/user-password-hash` |
| `admin-ssh-rsa/*` | `openssh-rsa/*` |
| `admin-ssh/*` | `openssh/*` |

Run `clan vars generate $MACHINE_NAME` after updating your configuration to generate the new vars.

## Complete Example

Here's a full migration example:

**Before:**

```nix
{
  flake.clan.inventory.instances = {
    admin = {
      roles.default.machines.my-server = { };
      roles.default.settings = {
        allowedKeys = {
          "admin-key" = "ssh-ed25519 AAAA...xyz admin@workstation";
        };
        certificateSearchDomains = [ "internal.example.com" ];
      };
    };
  };
}
```

**After:**

```nix
{
  flake.clan.inventory.instances = {
    sshd = {
      roles.server.machines.my-server = { };
      roles.server.settings = {
        authorizedKeys = {
          "admin-key" = "ssh-ed25519 AAAA...xyz admin@workstation";
        };
        certificate.searchDomains = [ "internal.example.com" ];
      };
      roles.client.machines.my-server = { };
    };

    root-password = {
      module = {
        name = "users";
        input = "clan-core";
      };
      roles.default.machines.my-server = { };
      roles.default.settings = {
        user = "root";
        prompt = true;
      };
    };
  };
}
```

## Additional sshd Features

The sshd service provides additional features not available in the admin service:

- **client role**: Configure machines to trust the SSH CA, enabling TOFU-less verification

See the [sshd service documentation](../../services/official/sshd.md) for details.
