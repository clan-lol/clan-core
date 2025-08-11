
A Dynamic-DNS (DDNS) service continuously keeps one or more DNS records in sync with the current public IP address of your machine.  
In *clan* this service is backed by [qdm12/ddns-updater](https://github.com/qdm12/ddns-updater).

> Info  
> ddns-updater itself is **heavily opinionated and version-specific**. Whenever you need the exhaustive list of flags or
> provider-specific fields refer to its *versioned* documentation – **not** the GitHub README
---

# 1. Configuration model

Internally ddns-updater consumes a single file named `config.json`.  
A minimal configuration for the registrar *Namecheap* looks like:

```json
{
  "settings": [
    {
      "provider": "namecheap",
      "domain": "sub.example.com",
      "password": "e5322165c1d74692bfa6d807100c0310"
    }
  ]
}
```

Another example for *Porkbun*:

```json
{
  "settings": [
    {
      "provider": "porkbun",
      "domain": "domain.com",
      "api_key": "sk1_…",
      "secret_api_key": "pk1_…",
      "ip_version": "ipv4",
      "ipv6_suffix": ""
    }
  ]
}
```

When you write a `clan.nix` the **common** fields (`provider`, `domain`, `period`, …) are already exposed as typed
*Nix options*.  
Registrar-specific or very new keys can be passed through an open attribute set called **extraSettings**.

---

# 2. Full Porkbun example

Manage three records – `@`, `home` and `test` – of the domain
`jon.blog` and refresh them every 15 minutes:

```nix title="clan.nix" hl_lines="10-11"
inventory.instances = {
  dyndns = {
    roles.default.machines."jon" = { };
    roles.default.settings = {
      period   = 15;                # minutes
      settings = {
        "all-jon-blog" = {
          provider         = "porkbun";
          domain           = "jon.blog";

          # (1) tell the secret-manager which key we are going to store
          secret_field_name = "secret_api_key";

          # everything below is copied verbatim into config.json
          extraSettings = {
            host         = "@,home,test";   # (2) comma-separated list of sub-domains
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

1. `secret_field_name` tells the *vars-generator* to store the entered secret under the specified JSON field name in the configuration.
2. ddns-updater allows multiple hosts by separating them with a comma.
3. The `api_key` above is *public*; the corresponding **private key** is retrieved through `secret_field_name`.

