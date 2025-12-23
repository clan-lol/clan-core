[ncps](https://github.com/kalbasit/ncps) is a high-performance proxy server that
accelerates Nix dependency retrieval across your local network by caching and
serving packages locally.

## Usage

```nix
inventory.instances = {
  ncps = {
    roles.server.machines."my-nas".settings = {
      cache.dataPath = "/srv/nas/var/lib/ncps";

        upstream = {
            caches = [
            "https://cache.nixos.org"
            "https://nix-community.cachix.org"
            "https://nixpkgs-unfree.cachix.org"
            "https://nix-gaming.cachix.org"
            "https://cuda-maintainers.cachix.org"
          ];

          publicKeys = [
            "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
            "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
            "nixpkgs-unfree.cachix.org-1:hqvoInulhbV4nJ9yJOEr+4wxhDV4xq2d1DK7S6Nj6rs="
            "nix-gaming.cachix.org-1:nbjlureqMbRAxR1gJ/f3hxemL9svXaZF/Ees8vCUUs4="
            "cuda-maintainers.cachix.org-1:0dq3bujKpuEPMCX6U4WylrUDZ9JyUG0VpVZa7CNfq5E="
          ];
      };
    }
    roles.client.machines."client".settings = {};
  };
};
```

Here `my-nas` is configured as the [ncps](https://github.com/kalbasit/ncps)
proxy-cache, intercepting all substitution requests from `client`, searches
binary caches for the requested package and download and serves it if found.

The advantage of this setup over a traditional binary cache is that all
retrieved packages are stored on `my-nas`, ready to serve other machines in your
clan.
