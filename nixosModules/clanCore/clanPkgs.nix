{ lib, pkgs, ... }:
{
  # TODO: Move this into settings.clanPkgs ?
  # This could also be part of the public interface to allow users to override the internal packages
  options.clan.core.clanPkgs = lib.mkOption {
    defaultText = "self.packages.${pkgs.stdenv.hostPlatform.system}";
    internal = true;
  };
}
