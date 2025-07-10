{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/trusted-nix-caches";
  manifest.description = "This module sets the `clan.lol` and `nix-community` cache up as a trusted cache.";
  manifest.categories = [ "System" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.default = {

    perInstance =
      { ... }:
      {
        nixosModule =
          { ... }:
          {
            nix.settings.trusted-substituters = [
              "https://cache.clan.lol"
              "https://nix-community.cachix.org"
            ];
            nix.settings.trusted-public-keys = [
              "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
              "cache.clan.lol-1:3KztgSAB5R1M+Dz7vzkBGzXdodizbgLXGXKXlcQLA28="
            ];
          };
      };
  };
}
