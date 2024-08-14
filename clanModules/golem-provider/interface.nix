{ lib, ... }:
let
  inherit (lib) mkOption;

  inherit (lib.types) nullOr str;

in
{
  options.clan.golem-provider = {
    account = mkOption {
      type = nullOr str;
      description = ''
        Ethereum address for payouts.

        Leave empty to automatically generate a new address upon first start.
      '';
      default = null;
    };
  };
}
