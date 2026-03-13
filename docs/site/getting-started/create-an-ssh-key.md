# Create an SSH Key

:::admonition[Tip]{type=tip}
Use this short guide to determine if you have an existing key pair, and if not, to create one.
:::

First, check for an existing key by typing:

```bash
ls ~/.ssh/id_ed25519*
```

If you see two files listed, id_ed25519 and id_ed25519.pub, you're good to go.

If you see `No such file or directory`, you need to create the pair.

To do so, type:

```bash
ssh-keygen -t ed25519
```

When prompted:
- File location: Press Enter to accept the default (~/.ssh/id_ed25519)
- Passphrase: Enter a passphrase or press Enter for none

This creates two files:
- ~/.ssh/id_ed25519 - Your private key (keep this secret!)
- ~/.ssh/id_ed25519.pub - Your public key (this gets shared with target machines)

Verify they exist by typing:

```bash
ls ~/.ssh/id_ed25519*
```

You should see both files listed.
