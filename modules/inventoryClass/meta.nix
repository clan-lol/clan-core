# This file is imported into:
# - clan.meta
# - clan.inventory.meta
{ config, lib, ... }:
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
      type = types.nullOr (types.strMatching "[a-z]+");
      default = null;
      example = "ccc";
      description = ''
        Deprecated: Use `domain` instead.
      '';
    };
    domain = lib.mkOption {
      type = types.strMatching "^[a-z0-9_]([a-z0-9_-]{0,61}[a-z0-9_])?(\.[a-z0-9_]([a-z0-9_-]{0,61}[a-z0-9_])?)*$";
      default =
        if config.tld != null then
          lib.warn "`clan.meta.tld` has been deprecated in favor of `clan.meta.domain`. `clan.meta.tld` will be removed in the next release." config.tld
        else
          "clan";
      defaultText = lib.literalExpression ''"clan"'';
      example = "clan.lol";
      description = ''
        Domain for the clan.

        It will be used to wire clan-internal services and resolve the address
        for each machine of the clan using `<hostname>.<meta.domain>`

        This can either be:

        - A top level domain (TLD). Set this to a valid, but not already
          existing TLD if you're using a mesh network between your machines.
          This will route requests between your machines over the mesh network.

        - A regular domain. Set this to a valid domain you own if you want
          to route requests between your machines over the public internet.
          You will have to manually setup your public DNS of that domain to
          route `<hostname>.<meta.domain>` to each of your machines.
      '';
    };
  };
in
{
  options = metaOptions;
}
