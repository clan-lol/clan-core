{
  config,
  lib,
  clanLib,
  ...
}:
{
  options.introspection = lib.mkOption {
    readOnly = true;
    # TODO: use options.inventory instead of the evaluate config attribute
    default =
      builtins.removeAttrs (clanLib.introspection.getPrios { options = config.inventory.options; })
        # tags are freeformType which is not supported yet.
        # services is removed and throws an error if accessed.
        [ "tags" "services"];
  };
}
