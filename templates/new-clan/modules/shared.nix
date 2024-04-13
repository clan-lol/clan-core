{clan-core, system, ...}:
{
  imports = [
    clan-core.clanModules.sshd
    clan-core.clanModules.diskLayouts
    clan-core.clanModules.root-password
  ];
  nixpkgs.hostPlatform = system;
}
