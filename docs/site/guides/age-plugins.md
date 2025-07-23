## Using Age Plugins

If you wish to use a key generated using an [age plugin] as your admin key, extra care is needed.

You must **precede your secret key with a comment that contains its corresponding recipient**.

This is usually output as part of the generation process
and is only required because there is no unified mechanism for recovering a recipient from a plugin secret key.

Here is an example:

```title="~/.config/sops/age/keys.txt"
# public key: age1zdy49ek6z60q9r34vf5mmzkx6u43pr9haqdh5lqdg7fh5tpwlfwqea356l
AGE-PLUGIN-FIDO2-HMAC-1QQPQZRFR7ZZ2WCV...
```

!!! note
    The comment that precedes the plugin secret key need only contain the recipient.
    Any other text is ignored.

    In the example above, you can specify `# recipient: age1zdy...`, `# public: age1zdy....` or even
    just `# age1zdy....`

You will need to add an entry into your `flake.nix` to ensure that the necessary `age` plugins
are loaded when using Clan:

```nix title="flake.nix"
{
  inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  inputs.nixpkgs.follows = "clan-core/nixpkgs";

  outputs =
    { self, clan-core, ... }:
    let
      # Sometimes this attribute set is defined in clan.nix
      clan = clan-core.lib.clan {
        inherit self;

        meta.name = "myclan";

        # Add Yubikey and FIDO2 HMAC plugins
        # Note: the plugins listed here must be available in nixpkgs.
        secrets.age.plugins = [
          "age-plugin-yubikey"
          "age-plugin-fido2-hmac"
        ];

        machines = {
          # elided for brevity
        };
      };
    in
    {
      inherit (clan) nixosConfigurations nixosModules clanInternals;

      # elided for brevity
    };
}
```
