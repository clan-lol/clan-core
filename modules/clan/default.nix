/**
  Root 'clan' Module

  Defines lib.clan and flake-parts.clan options
  and all common logic for the 'clan' module.

  - has Class _class = "clan"

  - _module.args.clan-core: reference to clan-core flake
  - _module.args.clanLib: reference to lib.clan function
*/
{ clan-core }:
{ lib, ... }:
let
  public = [
    "clanLib"
    "lib"
    "clan"
    "packages"
    "nixosModules"
    "darwinModules"
    # This is not strictly public
    # But annoying in traces, when evaluated by `lib.types.isType`
    "_type"
  ];
  public-clan-core = builtins.mapAttrs (
    attrName: v:
    lib.warnIf (!builtins.elem attrName public) ''
      Using deprecated clan-core attribute: '${attrName}'

      Only these attributes are officially supported:
        ${lib.concatStringsSep "\n  " public}

      If you need '${attrName}', please file an issue explaining your use case:
      https://git.clan.lol/clan/clan-core/issues
    '' v
  ) clan-core;
in
{
  _class = "clan";
  _module.args = {
    clan-core = public-clan-core;
    inherit (clan-core) clanLib;
  };
  imports = [
    ./top-level-interface.nix
    ./module.nix
    ./distributed-services.nix
    ./checks.nix
  ];
}
