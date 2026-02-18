---
a: 1
b: 2
---


## Generic code
```
nix run abc
```

## Language code
```js
const abc = 1 + "2";
const abc = 1 + "2";
const abc = 1 + "2";
const abc = 1 + "2";
```

## `choices.<name>.foo`

## Step Bar

```nix {1,18-21}
inventory.instances = {
  dyndns = {
    roles.default.machines."jon" = { }; # [!code --]
    roles.default.settings = { # [!code ++]
      period   = 15;                # minutes
      settings = {
        "all-jon-blog" = {
          provider         = "porkbun";
          domain           = "jon.blog";

          # (1) tell the secret-manager which key we are going to store
          secret_field_name = "secret_api_key";

          # everything below is copied verbatim into config.json
          extraSettings = {
            host         = "@,home,test";   # (2) comma-separated list of sub-domains [!code highlight]
            ip_version   = "ipv4";
            ipv6_suffix  = "";
            api_key      = "pk1_4bb2b231275a02fdc23b7e6f3552s01S213S"; # (3) public – safe to commit
          };
        };
      };
    };
  };
};
```

## Step Foo

Miscellaneous Symbols
☀ ☁ ☂ ☃ ☄ ★ ☆ ☇ ☈ ☉ ☊ ☋ ☌ ☍ ☎ ☏ ☐ ☑ ☒ ☓ ☚ ☛ ☜ ☝ ☞ ☟ ☠ ☡ ☢ ☣ ☤ ☥ ☦ ☧ ☨ ☩ ☪ ☫ ☬ ☭ ☮ ☯ ☰ ☱ ☲ ☳ ☴ ☵ ☶ ☷ ☸ ☹ ☺ ☻ ☼ ☽ ☾ ☿ ♀ ♁ ♂ ♃ ♄ ♅ ♆ ♇ ♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓ ♔ ♕ ♖ ♗ ♘ ♙ ♚ ♛ ♜ ♝ ♞ ♟ ♠ ♡ ♢ ♣ ♤ ♥ ♦ ♧ ♨ ♩ ♪ ♫ ♬ ♭ ♮ ♯

## Step Bar

↑
Duplicate heading, should still be linked

This is a divider

---

---

:::note[Note about nature]

Respect the nature of things

:::

::::important[Its important]

Follow this and your life will be happy

:::note
nested note probably a bad idea

but technically valid
:::

::::

:::danger[Attention Footgun]

Please don't erase your disk

```nix
erase = false;
```

:::

:::tip[Outsmart]

Lets be really clever

- List
- Inside

:::

This is a table

| A/B | A   | ¬A  |
| --- | --- | --- |
| B   | AB  | B   |
| ¬B  | A   | 0   |

## GFM

### Autolink literals

www.example.com, https://example.com, and contact@example.com.

### Footnote

A note[^1]

[^1]: Big note.

### Strikethrough

~one~ or ~~two~~ tildes.

### Table

| a   | b   |   c |  d  |
| --- | :-- | --: | :-: |
| 1   | 2   |   3 |  4  |

### Tasklist

- [ ] to do
- [x] done

* item
* normal
