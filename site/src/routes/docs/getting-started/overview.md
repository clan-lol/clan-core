---
a: 1
b: 2
---

# Getting Started Overview

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

## Step Bar
