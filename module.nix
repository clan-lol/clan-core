{ lib, ... }:
{
  _class = "clan.service";
  manifest.name = "test";

  roles.peer.interface =
    { ... }:
    {
      options.debug = lib.mkOption { default = 1; };
    };

  roles.peer.perInstance =
    { settings, ... }:
    {
      nixosModule = {
        options.debug = lib.mkOption {
          default = settings;
        };
      };
    };
}
