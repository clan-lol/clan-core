{
  lib,
  ...
}:
{
  imports = [
    (lib.mkRenamedOptionModule
      [ "clanCore" ]
      [
        "clan"
        "core"
      ]
    )
  ];

  options.clan.core.module = lib.mkOption {
    internal = true;
    type = lib.types.raw;
  };
}
