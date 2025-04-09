
Clan enables encryption of secrets (such as passwords & keys) ensuring security and ease-of-use among users.

By default, Clan uses the [sops](https://github.com/getsops/sops) format
and integrates with [sops-nix](https://github.com/Mic92/sops-nix) on NixOS machines.
Clan can also be configured to be used with other secret store [backends](https://docs.clan.lol/reference/clan-core/vars/#clan.core.vars.settings.secretStore).

This guide will walk you through:

- **Creating a Keypair for Your User**: Learn how to generate a keypair for `$USER` to securely control all secrets.
- **Creating Your First Secret**: Step-by-step instructions on creating your initial secret.
- **Assigning Machine Access to the Secret**: Understand how to grant a machine access to the newly created secret.

## Create Your Admin Keypair

To get started, you'll need to create **your admin keypair**.

!!! info
    Don't worry — if you've already made one before, this step won't change or overwrite it.

```bash
clan secrets key generate
```

**Output**:

```{.console, .no-copy}
Public key: age1wkth7uhpkl555g40t8hjsysr20drq286netu8zptw50lmqz7j95sw2t3l7

Generated age private key at '/home/joerg/.config/sops/age/keys.txt' for your user. Please back it up on a secure location or you will lose access to your secrets.
Also add your age public key to the repository with 'clan secrets users add YOUR_USER age1wkth7uhpkl555g40t8hjsysr20drq286netu8zptw50lmqz7j95sw2t3l7' (replace YOUR_USER with your actual username)
```

!!! warning
    Make sure to keep a safe backup of the private key you've just created.
    If it's lost, you won't be able to get to your secrets anymore because they all need the admin key to be unlocked.

If you already have an [age] secret key and want to use that instead, you can simply edit `~/.config/sops/age/keys.txt`:

```title="~/.config/sops/age/keys.txt"
AGE-SECRET-KEY-13GWMK0KNNKXPTJ8KQ9LPSQZU7G3KU8LZDW474NX3D956GGVFAZRQTAE3F4
```

Alternatively, you can provide your [age] secret key as an environment variable `SOPS_AGE_KEY`, or in a different file
using `SOPS_AGE_KEY_FILE`.
For more information see the [SOPS] guide on [encrypting with age].

!!! note
    It's safe to add any secrets created by the clan CLI and placed in your repository to version control systems like `git`.

### Using Age Plugins

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

### Add Your Public Key(s)

```console
clan secrets users add $USER --age-key <your_public_key>
```

It's best to choose the same username as on your Setup/Admin Machine that you use to control the deployment with.

Once run this will create the following files:

```{.console, .no-copy}
sops/
└── users/
    └── <your_username>/
        └── key.json
```
If you followed the quickstart tutorial all necessary secrets are initialized at this point.

!!! note
    You can add multiple age keys for a user by providing multiple `--age-key <your_public_key>` flags:

    ```console
    clan secrets users add $USER \
        --age-key <your_public_key_1> \
        --age-key <your_public_key_2> \
        ...
    ```

### Manage Your Public Key(s)

You can list keys for your user with `clan secrets users get $USER`:

```console
clan secrets users get alice

[
  {
    "publickey": "age1hrrcspp645qtlj29krjpq66pqg990ejaq0djcms6y6evnmgglv5sq0gewu",
    "type": "age",
    "username": "alice"
  },
  {
    "publickey": "age13kh4083t3g4x3ktr52nav6h7sy8ynrnky2x58pyp96c5s5nvqytqgmrt79",
    "type": "age",
    "username": "alice"
  }
]
```

To add a new key to your user:

```console
clan secrets users add-key $USER --age-key <your_public_key>
```

To remove a key from your user:

```console
clan secrets users remove-key $USER --age-key <your_public_key>
```

[age]: https://github.com/FiloSottile/age
[age plugin]: https://github.com/FiloSottile/awesome-age?tab=readme-ov-file#plugins
[sops]: https://github.com/getsops/sops
[encrypting with age]: https://github.com/getsops/sops?tab=readme-ov-file#encrypting-using-age
