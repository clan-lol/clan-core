# Advanced Vars Examples

This guide demonstrates complex, real-world patterns for the vars system. 


## Certificate Authority with Intermediate Certificates

This example shows how to create a complete certificate authority with root and intermediate certificates using dependencies.

```nix
{
  # Generate root CA (not deployed to machines)
  clan.core.vars.generators.root-ca = {
    files."ca.key" = {
      secret = true;
      deploy = false;  # Keep root key offline
    };
    files."ca.crt".secret = false;
    runtimeInputs = [ pkgs.step-cli ];
    script = ''
      step certificate create "My Root CA" \
        $out/ca.crt $out/ca.key \
        --profile root-ca \
        --no-password \
        --not-after 87600h
    '';
  };

  # Generate intermediate key
  clan.core.vars.generators.intermediate-key = {
    files."intermediate.key" = {
      secret = true;
      deploy = true;
    };
    runtimeInputs = [ pkgs.step-cli ];
    script = ''
      step crypto keypair \
        $out/intermediate.pub \
        $out/intermediate.key \
        --no-password
    '';
  };

  # Generate intermediate certificate signed by root
  clan.core.vars.generators.intermediate-cert = {
    files."intermediate.crt".secret = false;
    dependencies = [
      "root-ca"
      "intermediate-key"
    ];
    runtimeInputs = [ pkgs.step-cli ];
    script = ''
      step certificate create "My Intermediate CA" \
        $out/intermediate.crt \
        $in/intermediate-key/intermediate.key \
        --ca $in/root-ca/ca.crt \
        --ca-key $in/root-ca/ca.key \
        --profile intermediate-ca \
        --not-after 8760h \
        --no-password
    '';
  };

  # Use the certificates in services
  services.nginx.virtualHosts."example.com" = {
    sslCertificate = config.clan.core.vars.generators.intermediate-cert.files."intermediate.crt".value;
    sslCertificateKey = config.clan.core.vars.generators.intermediate-key.files."intermediate.key".path;
  };
}
```

## Multi-Service Secret Sharing

Generate secrets that multiple services can use:

```nix
{
  # Generate database credentials
  clan.core.vars.generators.database = {
    share = true;  # Share across machines
    files."password" = { };
    files."connection-string" = { };
    prompts.dbname = {
      description = "Database name";
      type = "line";
    };
    script = ''
      # Generate password
      tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32 > $out/password
      
      # Create connection string
      echo "postgresql://app:$(cat $out/password)@localhost/$prompts/dbname" \
        > $out/connection-string
    '';
  };

  # PostgreSQL uses the password
  services.postgresql = {
    enable = true;
    initialScript = pkgs.writeText "init.sql" ''
      CREATE USER app WITH PASSWORD '${
        builtins.readFile config.clan.core.vars.generators.database.files."password".path
      }';
    '';
  };

  # Application uses the connection string
  systemd.services.myapp = {
    serviceConfig.EnvironmentFile = 
      config.clan.core.vars.generators.database.files."connection-string".path;
  };
}
```

## SSH Host Keys with Certificates

Generate SSH host keys and sign them with a CA:

```nix
{
  # SSH Certificate Authority (shared)
  clan.core.vars.generators.ssh-ca = {
    share = true;
    files."ca" = { secret = true; deploy = false; };
    files."ca.pub" = { secret = false; };
    runtimeInputs = [ pkgs.openssh ];
    script = ''
      ssh-keygen -t ed25519 -N "" -f $out/ca
      mv $out/ca.pub $out/ca.pub
    '';
  };

  # Host-specific SSH keys
  clan.core.vars.generators.ssh-host = {
    files."ssh_host_ed25519_key" = {
      secret = true;
      owner = "root";
      group = "root";
      mode = "0600";
    };
    files."ssh_host_ed25519_key.pub" = { secret = false; };
    files."ssh_host_ed25519_key-cert.pub" = { secret = false; };
    dependencies = [ "ssh-ca" ];
    runtimeInputs = [ pkgs.openssh ];
    script = ''
      # Generate host key
      ssh-keygen -t ed25519 -N "" -f $out/ssh_host_ed25519_key
      
      # Sign with CA
      ssh-keygen -s $in/ssh-ca/ca \
        -I "host:${config.networking.hostName}" \
        -h \
        -V -5m:+365d \
        $out/ssh_host_ed25519_key.pub
    '';
  };

  # Configure SSH to use the generated keys
  services.openssh = {
    hostKeys = [{
      path = config.clan.core.vars.generators.ssh-host.files."ssh_host_ed25519_key".path;
      type = "ed25519";
    }];
  };
}
```

## WireGuard Mesh Network

Create a WireGuard configuration with pre-shared keys:

```nix
{
  # Generate WireGuard keys for this host
  clan.core.vars.generators.wireguard = {
    files."privatekey" = {
      secret = true;
      owner = "systemd-network";
      mode = "0400";
    };
    files."publickey" = { secret = false; };
    files."preshared" = { secret = true; };
    runtimeInputs = [ pkgs.wireguard-tools ];
    script = ''
      # Generate key pair
      wg genkey > $out/privatekey
      wg pubkey < $out/privatekey > $out/publickey
      
      # Generate pre-shared key
      wg genpsk > $out/preshared
    '';
  };

  # Configure WireGuard
  networking.wireguard.interfaces.wg0 = {
    privateKeyFile = config.clan.core.vars.generators.wireguard.files."privatekey".path;
    
    peers = [{
      publicKey = "peer-public-key-here";
      presharedKeyFile = config.clan.core.vars.generators.wireguard.files."preshared".path;
      allowedIPs = [ "10.0.0.2/32" ];
    }];
  };
}
```

## Conditional Generation Based on Machine Role

Generate different secrets based on machine configuration:

```nix
{
  clan.core.vars.generators = lib.mkMerge [
    # All machines get basic auth
    {
      basic-auth = {
        files."htpasswd" = { };
        prompts.username = {
          description = "Username for basic auth";
          type = "line";
        };
        prompts.password = {
          description = "Password for basic auth";
          type = "hidden";
        };
        runtimeInputs = [ pkgs.apacheHttpd ];
        script = ''
          htpasswd -nbB "$prompts/username" "$prompts/password" > $out/htpasswd
        '';
      };
    }

    # Only servers get API tokens
    (lib.mkIf config.services.myapi.enable {
      api-tokens = {
        files."admin-token" = { };
        files."readonly-token" = { };
        runtimeInputs = [ pkgs.openssl ];
        script = ''
          openssl rand -hex 32 > $out/admin-token
          openssl rand -hex 16 > $out/readonly-token
        '';
      };
    })
  ];
}
```

## Backup Encryption Keys

Generate and manage backup encryption keys:

```nix
{
  clan.core.vars.generators.backup = {
    share = true;  # Same key for all backup sources
    files."encryption.key" = {
      secret = true;
      deploy = true;
    };
    files."encryption.pub" = { secret = false; };
    runtimeInputs = [ pkgs.age ];
    script = ''
      # Generate age key pair
      age-keygen -o $out/encryption.key 2>/dev/null
      
      # Extract public key
      grep "public key:" $out/encryption.key | cut -d: -f2 | tr -d ' ' \
        > $out/encryption.pub
    '';
  };

  # Use in backup service
  services.borgbackup.jobs.system = {
    encryption = {
      mode = "repokey-blake2";
      passCommand = "cat ${config.clan.core.vars.generators.backup.files."encryption.key".path}";
    };
  };
}
```

## Tips and Best Practices

1. **Use dependencies** to build complex multi-stage generations
2. **Share generators** when the same secret is needed across machines
3. **Set appropriate permissions** for service-specific secrets
4. **Use prompts** for user-specific values that shouldn't be generated
5. **Combine secret and non-secret files** in the same generator when they're related
6. **Use conditional generation** with `lib.mkIf` for role-specific secrets