{
  config,
  clan-core,
  # Optional, if you want to access other flakes:
  # self,
  ...
}:
{
  imports = [
    clan-core.clanModules.user-password
  ];

  # Locale service discovery and mDNS
  services.avahi.enable = true;

  # generate a random password for our user below
  # can be read using `clan secrets get <machine-name>-user-password` command
  clan.user-password.user = "user";
  users.users.user = {
    isNormalUser = true;
    extraGroups = [
      "wheel"
      "networkmanager"
      "video"
      "input"
    ];
    uid = 1000;
  };
}
