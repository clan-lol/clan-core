{ lib, ... }:
let
  optStr = lib.types.nullOr lib.types.str;
in
{
  options.clan.meta.name = lib.mkOption { type = lib.types.str; };
  options.clan.meta.description = lib.mkOption { type = optStr; };
  options.clan.meta.icon = lib.mkOption { type = optStr; };
}
