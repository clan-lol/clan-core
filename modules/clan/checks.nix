{ lib, nixpkgs, ... }:
{
  checks.minNixpkgsVersion = {
    assertion = lib.versionAtLeast nixpkgs.lib.version "25.11";
    message = ''
      Nixpkgs version: ${nixpkgs.lib.version} is incompatible with clan-core. (>= 25.11 is recommended)
      ---
      Your version of 'nixpkgs' seems too old for clan-core.
      Please read: https://docs.clan.lol/guides/nixpkgs-flake-input

      You can ignore this check by setting:
      clan.checks.minNixpkgsVersion.ignore = true;
      ---
    '';
  };
}
