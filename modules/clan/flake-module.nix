{ self, lib, ... }:
{
  flake.modules.clan.default = lib.modules.importApply ./default.nix { clan-core = self; };
}
