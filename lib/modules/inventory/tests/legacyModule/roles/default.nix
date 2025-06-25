{
  lib,
  clan-core,
  ...
}:
{
  # Just some random stuff
  options.test = lib.mapAttrs clan-core;
}
