{ lib, ... }:
{
  options = {
    clan.core.sops.defaultGroups = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      example = [ "admins" ];
      description = "The default groups to for encryption use when no groups are specified.";
    };
  };
}
