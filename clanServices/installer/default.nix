# Example clan service. See https://docs.clan.lol/guides/services/community/
# for more details

# The test for this module in ./tests/vm/default.nix shows an example of how
# the service is used.
{
  clanPackages,
  ...
}:
{
  lib,
  clanLib,
  ...
}:
{
  _class = "clan.service";
  manifest.name = "clan-core/installer";
  manifest.description = "A service that turns target machines into an installer image.";
  manifest.readme = builtins.readFile ./README.md;

  roles.iso = {
    description = "Makes a machine an ISO installer machine";

    perInstance =
      {
        exports,
        machine,
        ...
      }:
      let
        # Select tor server exports for this machine only
        torExports = clanLib.selectExports (
          scope:
          scope.serviceName == "clan-core/tor"
          && scope.roleName == "server"
          && scope.machineName == machine.name
        ) exports;

        # Extract tor instance names from scope keys
        torInstanceNames = lib.mapAttrsToList (
          scopeKey: _: (clanLib.parseScope scopeKey).instanceName
        ) torExports;
      in
      {
        nixosModule =
          { lib, pkgs, ... }:
          {
            imports = [
              (lib.modules.importApply ./nixos-image/image-installer/module.nix {
                network-status = clanPackages.${pkgs.stdenv.hostPlatform.system}.network-status;
                inherit torInstanceNames;
              })
            ];
          };
      };
  };
}
