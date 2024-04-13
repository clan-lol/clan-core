{ clan-core, ... }:
{
  imports = [
    clan-core.clanModules.sshd
    clan-core.clanModules.diskLayouts
    clan-core.clanModules.root-password
  ];
}
