# Troubleshooting Vars

Quick reference for diagnosing and fixing vars issues.

## Common Issues

### Generator Script Fails

**Symptom**: Error during `clan vars generate` or deployment

**Possible causes and solutions**:

1. **Missing runtime inputs**
   ```nix
   # Wrong - missing required tool
   runtimeInputs = [ ];
   script = ''
     openssl rand -hex 32 > $out/secret  # openssl not found!
   '';
   
   # Correct
   runtimeInputs = [ pkgs.openssl ];
   ```

2. **Wrong output path**
   ```nix
   # Wrong - must use $out
   script = ''
     echo "secret" > ./myfile
   '';
   
   # Correct
   script = ''
     echo "secret" > $out/myfile
   '';
   ```

3. **Missing declared files**
   ```nix
   files."config" = { };
   files."key" = { };
   script = ''
     # Wrong - only generates one file
     echo "data" > $out/config
   '';
   
   # Correct - must generate all declared files
   script = ''
     echo "data" > $out/config
     echo "key" > $out/key
   '';
   ```

### Cannot Access Generated Files

**Symptom**: "attribute 'value' missing" or file not found

**Solutions**:

1. **Secret files don't have `.value`**
   ```nix
   # Wrong - secret files can't use .value
   files."secret" = { secret = true; };
   # ...
   environment.etc."app.conf".text = 
     config.clan.core.vars.generators.app.files."secret".value;
   
   # Correct - use .path for secrets
   environment.etc."app.conf".source = 
     config.clan.core.vars.generators.app.files."secret".path;
   ```

2. **Public files should use `.value`**
   ```nix
   # Better for non-secrets
   files."cert.pem" = { secret = false; };
   # ...
   sslCertificate = 
     config.clan.core.vars.generators.ca.files."cert.pem".value;
   ```

### Dependencies Not Available

**Symptom**: "No such file or directory" when accessing `$in/...`

**Solution**: Declare dependencies correctly
```nix
clan.core.vars.generators.child = {
  # Wrong - missing dependency
  script = ''
    cat $in/parent/file > $out/newfile
  '';
  
  # Correct
  dependencies = [ "parent" ];
  script = ''
    cat $in/parent/file > $out/newfile
  '';
};
```

### Permission Denied

**Symptom**: Service cannot read generated secret file

**Solution**: Set correct ownership and permissions
```nix
files."service.key" = {
  secret = true;
  owner = "myservice";  # Match service user
  group = "myservice";
  mode = "0400";       # Read-only for owner
};
```

### Vars Not Regenerating

**Symptom**: Changes to generator script don't trigger regeneration

**Solution**: Use `--regenerate` flag
```bash
clan vars generate my-machine --generator my-generator --regenerate
```

### Prompts Not Working

**Symptom**: Script fails with "No such file or directory" for prompts

**Solution**: Access prompts correctly
```nix
# Wrong
script = ''
  echo $password > $out/file
'';

# Correct
prompts.password.type = "hidden";
script = ''
  cat $prompts/password > $out/file
'';
```

## Debugging Techniques

### 1. Check Generator Status

See what vars are set:
```bash
clan vars list my-machine
```

### 2. Inspect Generated Files

For shared vars:
```bash
ls -la vars/shared/my-generator/
```

For per-machine vars:
```bash
ls -la vars/per-machine/my-machine/my-generator/
```

### 3. Test Generators Locally

Create a test script to debug:
```nix
# test-generator.nix
{ pkgs ? import <nixpkgs> {} }:
pkgs.stdenv.mkDerivation {
  name = "test-generator";
  buildInputs = [ pkgs.openssl ];  # Your runtime inputs
  buildCommand = ''
    # Your generator script here
    mkdir -p $out
    openssl rand -hex 32 > $out/secret
    ls -la $out/
  '';
}
```

Run with:
```bash
nix-build test-generator.nix
```

### 4. Enable Debug Logging

Set debug mode:
```bash
clan --debug vars generate my-machine
```

### 5. Check File Permissions

Verify generated secret permissions:
```bash
# On the target machine
ls -la /run/secrets/
```

## Recovery Procedures

### Regenerate All Vars

If vars are corrupted or need refresh:
```bash
# Regenerate all for a machine
clan vars generate my-machine --regenerate

# Regenerate specific generator
clan vars generate my-machine --generator my-generator --regenerate
```

### Manual Secret Injection

For recovery or testing:
```bash
# Set a var manually (bypass generator)
echo "temporary-secret" | clan vars set my-machine my-generator/my-file
```

### Restore from Backup

Vars are stored in the repository:
```bash
# Restore previous version
git checkout HEAD~1 -- vars/

# Check and regenerate if needed
clan vars list my-machine
```

## Storage Backend Issues

### SOPS Decryption Fails

**Symptom**: "Failed to decrypt" or permission errors

**Solution**: Ensure your user/machine has the correct age keys configured. Clan manages encryption keys automatically based on the configured users and machines in your flake.

Check that:

1. Your machine is properly configured in the flake
  
2. Your user has access to the machine's secrets
   
3. The age key is available in the expected location

### Password Store Issues

**Symptom**: "pass: store not initialized"

**Solution**: Initialize password store:
```bash
export PASSWORD_STORE_DIR=/path/to/clan/vars
pass init your-gpg-key
```

## Getting Help

If these solutions don't resolve your issue:

1. Check the [clan-core issue tracker](https://git.clan.lol/clan/clan-core/issues)
2. Ask in the Clan community channels
3. Provide:
  
     - The generator configuration

     - The exact error message

     - Output of `clan --debug vars generate`