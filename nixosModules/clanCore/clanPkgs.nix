{ lib, pkgs, ... }:
{
  options.clan.core.clanPkgs = lib.mkOption {
    defaultText = "self.packages.${pkgs.stdenv.hostPlatform.system}";
    internal = true;
    apply =
      v:
      lib.warn ''
        'clan.core.clanPkgs' is deprecated and will be removed in the next release.

        If you reference 'clanPkgs.zerotier-members' or 'clanPkgs.zerotierone'
        See the [zerotier-migration guide](https://clan.lol/docs/unstable/guides/migrations/zerotier)

        If you reference any other attribute contact us on matrix: https://matrix.to/#/#clan:clan.lol
      '' v;
  };
}
