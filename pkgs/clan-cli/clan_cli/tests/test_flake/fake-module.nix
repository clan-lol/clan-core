{ lib, ... }:
{
  options.clan.fake-module.fake-flag = lib.mkOption {
    type = lib.types.bool;
    default = false;
    description = ''
      A useless fake flag fro testing purposes.
    '';
  };
}
