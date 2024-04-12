{ pkgs, config, ... }:
{
  users.mutableUsers = false;
  users.users.root.hashedPasswordFile =
    config.clanCore.facts.services.root-password.secret.password-hash.path;
  sops.secrets."${config.clanCore.machineName}-password-hash".neededForUsers = true;
  clanCore.facts.services.root-password = {
    secret.password = { };
    secret.password-hash = { };
    generator.path = with pkgs; [
      coreutils
      xkcdpass
      mkpasswd
    ];
    generator.script = ''
      xkcdpass --numwords 3 --delimiter - --count 1 > $secrets/password
      cat $secrets/password | mkpasswd -s -m sha-512 > $secrets/password-hash
    '';
  };
}
