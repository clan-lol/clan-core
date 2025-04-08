{ lib, ... }:
{
  options.clan.jitsi.enable = lib.mkOption {
    type = lib.types.bool;
    default = false;
    description = "Enable jitsi on this machine";
  };
}
