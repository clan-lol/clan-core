# Example clan service. See https://docs.clan.lol/guides/services/community/
# for more details

# The test for this module in ./tests/vm/default.nix shows an example of how
# the service is used.
{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/installer";
  manifest.description = "A service that turns target machines into an installer image.";
  manifest.readme = builtins.readFile ./README.md;

  roles.iso = {
    description = "Makes a machine an ISO installer machine";

    perInstance = _: {
      nixosModule = ./nixos-image/image-installer/module.nix;
    };
  };
}
