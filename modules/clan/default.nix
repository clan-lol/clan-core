/**
  Root 'clan' Module

  Defines lib.clan and flake-parts.clan options
  and all common logic for the 'clan' module.

  - has Class _class = "clan"

  - _module.args.clan-core: reference to clan-core flake
  - _module.args.clanLib: reference to lib.clan function
*/
{ clan-core }:
{
  _class = "clan";
  _module.args = {
    inherit clan-core;
    inherit (clan-core) clanLib;
  };
  imports = [
    ./top-level-interface.nix
    ./module.nix
    ./distributed-services.nix
    ./checks.nix
  ];
}
