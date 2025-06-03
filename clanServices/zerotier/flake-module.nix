{
  lib,
  ...
}:
{
  clan.modules = {
    zerotier = lib.modules.importApply ./default.nix { };
  };
}
