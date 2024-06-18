{ config, pkgs, ... }:
{
  services.openssh.enable = true;
  services.openssh.settings.PasswordAuthentication = false;

  services.openssh.hostKeys = [
    {
      path = config.clan.core.facts.services.openssh.secret."ssh.id_ed25519".path;
      type = "ed25519";
    }
  ];

  clan.core.facts.services.openssh = {
    secret."ssh.id_ed25519" = { };
    public."ssh.id_ed25519.pub" = { };
    generator.path = [
      pkgs.coreutils
      pkgs.openssh
    ];
    generator.script = ''
      ssh-keygen -t ed25519 -N "" -f $secrets/ssh.id_ed25519
      mv $secrets/ssh.id_ed25519.pub $facts/ssh.id_ed25519.pub
    '';
  };
}
