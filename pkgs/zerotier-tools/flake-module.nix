{
  perSystem =
    { config, ... }:
    {
      checks = config.packages.zerotier-tools.tests;
    };
}
