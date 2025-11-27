# Using Age Plugins with Clan Vars

This guide explains how to set up YubiKey and other plugins for `clan vars` secrets.

By default the `clan vars` subcommand uses the `age` encryption tool, which supports various plugins.

---

## Supported Age Plugins

Below is a [list of popular `age` plugins](https://github.com/FiloSottile/awesome-age?tab=readme-ov-file#plugins) you can use with Clan. (Last updated: **September 12, 2025**)

- ⭐️ [**age-plugin-yubikey**](https://github.com/str4d/age-plugin-yubikey): YubiKey (and other PIV tokens) plugin.
-  [**age-plugin-se**](https://github.com/remko/age-plugin-se): Apple Secure Enclave plugin.
- 🧪 [**age-plugin-tpm**](https://github.com/Foxboron/age-plugin-tpm): TPM 2.0 plugin.
- 🧪 [**age-plugin-tkey**](https://github.com/quite/age-plugin-tkey): Tillitis TKey plugin.
   [**age-plugin-trezor**](https://github.com/romanz/trezor-agent/blob/master/doc/README-age.md): Hardware wallet plugin (TREZOR, Ledger, etc.).
- 🧪 [**age-plugin-sntrup761x25519**](https://github.com/keisentraut/age-plugin-sntrup761x25519): Post-quantum hybrid plugin (NTRU Prime + X25519).
- 🧪 [**age-plugin-fido**](https://github.com/riastradh/age-plugin-fido): Prototype symmetric encryption plugin for FIDO2 keys.
- 🧪 [**age-plugin-fido2-hmac**](https://github.com/olastor/age-plugin-fido2-hmac): FIDO2 plugin with PIN support.
- 🧪 [**age-plugin-sss**](https://github.com/olastor/age-plugin-sss): Shamir's Secret Sharing (SSS) plugin.
- 🧪 [**age-plugin-amnesia**](https://github.com/cedws/amnesia/blob/master/README.md#age-plugin-experimental): Adds Q&A-based identity wrapping.

> **Note:** Plugins marked with 🧪 are experimental. Plugins marked with ⭐️ are official.

---

## Using Plugin-Generated Keys

If you want to use `fido2 tokens` to encrypt your secret instead of the normal age secret key then you need to prefix your age secret key with the corresponding plugin name. In our case we want to use the `age-plugin-fido2-hmac` plugin so we replace `AGE-SECRET-KEY` with `AGE-PLUGIN-FIDO2-HMAC`.

??? tip
    - On Linux the age secret key is located at `~/.config/sops/age/keys.txt`
    - On macOS it is located at `/Users/admin/Library/Application Support/sops/age/keys.txt`

**Before**:
  ```hl_lines="2"
  # public key: age1zdy49ek6z60q9r34vf5mmzkx6u43pr9haqdh5lqdg7fh5tpwlfwqea356l
  AGE-SECRET-KEY-1QQPQZRFR7ZZ2WCV...
  ```

  **After**:
```hl_lines="2"
# public key: age1zdy49ek6z60q9r34vf5mmzkx6u43pr9haqdh5lqdg7fh5tpwlfwqea356l
AGE-PLUGIN-FIDO2-HMAC-1QQPQZRFR7ZZ2WCV...
```



## Configuring Plugins in `flake.nix`

To use `age` plugins with Clan, you need to configure them in your `flake.nix` file. Here’s an example:

```nix title="flake.nix"
{
  inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  inputs.nixpkgs.follows = "clan-core/nixpkgs";

  outputs = { self, clan-core, ... }:
  let
    # Define Clan configuration
    clan = clan-core.lib.clan {
      inherit self;

      meta.name = "myclan";
      meta.domain = "ccc";

      # Add YubiKey and FIDO2 HMAC plugins
      # Note: Plugins must be available in nixpkgs.
      secrets.age.plugins = [
        "age-plugin-yubikey"
        "age-plugin-fido2-hmac"
      ];

      machines = {
        # Machine configurations (elided for brevity)
      };
    };
  in
  {
    inherit (clan) nixosConfigurations nixosModules clanInternals;

    # Additional configurations (elided for brevity)
  };
}
```
