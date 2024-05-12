{ clan-core, ... }:
{
  imports = [
    clan-core.clanModules.sshd
    clan-core.clanModules.root-password
  ];

  # Locale service discovery and mDNS
  services.avahi.enable = true;
}
