# This file contains dependency option declarations
# Those need to be injected from a higher-level module
# For example, clan/module.nix injects 'clanConfig' into each machine
{ lib, ... }:
let
  inherit (lib) mkOption;
  inherit (lib.types) raw;
in
{
  options.clanConfig = mkOption {
    type = raw;
    description = ''
      The clan configuration from the outer clan module.

      i.e. defined in your 'flake.nix' or 'clan.nix' as

      ```nix
      clan = {
        meta.name = "my-clan-config";
        ...
      }
      ```
    '';
    readOnly = true;
  };
}
