{ packages }:
{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/zerotier";

  # TODO: Migrate the behavior from nixosModules/clanCore/zerotier
  # Expose a flag, to disable the clanCore/zerotier module if this module is used
  # To ensure conflict free behavior
  roles.moon = { };
  roles.peer = { };
  roles.controller = { };
}
