# This file is imported into:
# - clan.meta
# - clan.inventory.meta
{ lib, ... }:
let
  types = lib.types;

  metaOptions = {
    name = lib.mkOption {
      type = types.strMatching "[a-zA-Z0-9_-]*";
      example = "my_clan";
      description = ''
        Name of the clan.

        Needs to be (globally) unique, as this determines the folder name where the flake gets downloaded to.

        Should only contain alphanumeric characters, `_` and `-`.
      '';
    };
    description = lib.mkOption {
      default = null;
      type = types.nullOr types.str;
      description = ''
        Optional freeform description
      '';
    };
    icon = lib.mkOption {
      default = null;
      type = types.nullOr types.str;
      description = ''
        Under construction, will be used for the UI
      '';
    };
    tld = lib.mkOption {
      type = types.strMatching "[a-z]+";
      default = "clan";
      example = "ccc";
      description = ''
        Top level domain (TLD) of the clan. It should be set to a valid, but
        not already existing TLD.

        It will be used to provide clan-internal services and resolve each host of the
        clan with:

        <hostname>.<tld>
      '';
    };
  };
in
{
  options = metaOptions;
}
