{ lib
, pkgs
, ...
}: {
  systemd.tmpfiles.rules = [
    "d /var/shared 0777 root root - -"
  ];
  services.openssh.settings.PermitRootLogin = "yes";
  system.activationScripts.root-password = ''
    mkdir -p /var/shared
    ${pkgs.pwgen}/bin/pwgen -s 16 1 > /var/shared/root-password
    echo "root:$(cat /var/shared/root-password)" | chpasswd
  '';
  hidden-announce = {
    enable = true;
    script = pkgs.writers.writeDash "write-hostname" ''
      mkdir -p /var/shared
      echo "$1" > /var/shared/onion-hostname
    '';
  };
  services.getty.autologinUser = lib.mkForce "root";
  programs.bash.interactiveShellInit = ''
    if [ "$(tty)" = "/dev/tty1" ]; then
      until test -e /var/shared/onion-hostname; do sleep 1; done
      echo "ssh://root:$(cat /var/shared/root-password)@$(cat /var/shared/onion-hostname)"
    fi
  '';
  formatConfigs.install-iso = {
    isoImage.squashfsCompression = "zstd -Xcompression-level 1";
  };
}
