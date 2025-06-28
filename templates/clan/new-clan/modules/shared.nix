{
  config,
  clan-core,
  # Optional, if you want to access other flakes:
  # self,
  ...
}:
{
  imports = [
    # Enables the OpenSSH server for remote access
    clan-core.clanModules.sshd
    # Set a root password
    clan-core.clanModules.root-password
    clan-core.clanModules.user-password
    clan-core.clanModules.state-version

    # You can access other flakes imported in your flake via `self` like this:
    # self.inputs.nix-index-database.nixosModules.nix-index
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
    openssh.authorizedKeys.keys = config.users.users.root.openssh.authorizedKeys.keys;
  };
}
