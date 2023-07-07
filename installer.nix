{ config, lib, pkgs, ... }:
{
  systemd.tmpfiles.rules = [
    "d /var/shared 0777 root root - -"
  ];
  services.openssh.settings.PermitRootLogin = "yes";
  system.activationScripts.root-password = ''
    ${pkgs.pwgen}/bin/pwgen -s 16 1 > /var/shared/root-password
    echo "root:$(cat /var/shared/root-password)" | chpasswd
  '';
  hidden-announce = {
    enable = true;
    script = pkgs.writers.writeDash "write-hostname" ''
      echo "$1" > /var/shared/onion-hostname
    '';
  };
  services.getty.autologinUser = lib.mkForce "root";
  programs.bash.interactiveShellInit = ''
    if [ "$(tty)" = "/dev/tty1" ]; then
      echo "ssh://root:$(cat /var/shared/root-password)@$(cat /var/shared/onion-hostname)"
    fi
  '';
  # TODO find a place to put this
  # isoImage.squashfsCompression = "zstd -Xcompression-level 1";
}
