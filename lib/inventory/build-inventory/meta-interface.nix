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
  };
in
{
  options = metaOptions;
}
