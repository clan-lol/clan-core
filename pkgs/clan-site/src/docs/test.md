# Test

## Code

```
nix run abc
```

## Code for a language

```js
const abc = 1 + "2";
const abc = 1 + "2";
const abc = 1 + "2";
const abc = 1 + "2";
```

## Code Highlighting

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

## Code Title
```nix [nixos.nix] {2}
{
  foo = "bar";
  bar = "foo";
}
```

## Title with inline code `choices.<name>.foo`

## Step Foo

Miscellaneous Symbols
☀ ☁ ☂ ☃ ☄ ★ ☆ ☇ ☈ ☉ ☊ ☋ ☌ ☍ ☎ ☏ ☐ ☑ ☒ ☓ ☚ ☛ ☜ ☝ ☞ ☟ ☠ ☡ ☢ ☣ ☤ ☥ ☦ ☧ ☨ ☩ ☪ ☫ ☬ ☭ ☮ ☯ ☰ ☱ ☲ ☳ ☴ ☵ ☶ ☷ ☸ ☹ ☺ ☻ ☼ ☽ ☾ ☿ ♀ ♁ ♂ ♃ ♄ ♅ ♆ ♇ ♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓ ♔ ♕ ♖ ♗ ♘ ♙ ♚ ♛ ♜ ♝ ♞ ♟ ♠ ♡ ♢ ♣ ♤ ♥ ♦ ♧ ♨ ♩ ♪ ♫ ♬ ♭ ♮ ♯

↑
Duplicate heading, should still be linked

This is a divider

---

---

## Admonition

:::admonition[Note about nature]

Respect the nature of things

:::

## Nested Admonition
::::admonition[Its important]{type=important}

Follow this and your life will be happy

:::admonition{type=note}
nested note probably a bad idea

but technically valid
:::

::::

:::admonition[Attention Footgun]{type=danger}

Please don't erase your disk

```nix
erase = false;
```

:::

## Collapsible Admonition
:::admonition[Outsmart]{type=tip collapsed}

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
