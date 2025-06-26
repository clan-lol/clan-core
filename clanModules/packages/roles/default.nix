{
  config,
  lib,
  pkgs,
  ...
}:
{
  options.clan.packages = {
    packages = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      description = "The packages to install on the machine";
    };
  };
  config = {

    warnings = [
      "The clan.packages module is deprecated and will be removed on 2025-07-15.
      Please migrate to user-maintained configuration or the new equivalent clan services
      (https://docs.clan.lol/reference/clanServices)."
    ];
    environment.systemPackages = map (
      pName: lib.getAttrFromPath (lib.splitString "." pName) pkgs
    ) config.clan.packages.packages;
  };
}
