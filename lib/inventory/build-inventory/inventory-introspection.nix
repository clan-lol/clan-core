{ clanLib }:
{
  config,
  options,
  lib,
  ...
}:
{
  options.introspection = lib.mkOption {
    readOnly = true;
    # TODO: use options.inventory instead of the evaluate config attribute
    default =
      builtins.removeAttrs (clanLib.introspection.getPrios { options = config.inventory.options; })
        # tags are freeformType which is not supported yet.
        [ "tags" ];
  };
}
