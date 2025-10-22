{ lib, ... }:
{
  options.testDebug = lib.mkOption {
    default = 42;
  };
}
