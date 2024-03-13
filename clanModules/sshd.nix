{ config, pkgs, ... }: {
  services.openssh.enable = true;

  services.openssh.hostKeys = [{
    path = config.clanCore.secrets.openssh.secrets."ssh.id_ed25519".path;
    type = "ed25519";
  }];

  clanCore.secrets.openssh = {
    secrets."ssh.id_ed25519" = { };
    facts."ssh.id_ed25519.pub" = { };
    generator.path = [ pkgs.coreutils pkgs.openssh ];
    generator.script = ''
      ssh-keygen -t ed25519 -N "" -f $secrets/ssh.id_ed25519
      mv $secrets/ssh.id_ed25519.pub $facts/ssh.id_ed25519.pub
    '';
  };
}
