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
  hidden-ssh-announce = {
    enable = true;
    script = pkgs.writers.writeDash "write-hostname" ''
      mkdir -p /var/shared
      echo "$1" > /var/shared/onion-hostname
      ${pkgs.jq}/bin/jq -nc \
        --arg password "$(cat /var/shared/root-password)" \
        --arg address "$(cat /var/shared/onion-hostname)" '{
          password: $password, address: $address
        }' > /var/shared/login.info
      cat /var/shared/login.info |
        ${pkgs.qrencode}/bin/qrencode -t utf8 > /var/shared/qrcode.utf8
      cat /var/shared/login.info |
        ${pkgs.qrencode}/bin/qrencode -t png > /var/shared/qrcode.png
    '';
  };
  services.getty.autologinUser = lib.mkForce "root";
  programs.bash.interactiveShellInit = ''
    if [ "$(tty)" = "/dev/tty1" ]; then
      until test -e /var/shared/qrcode.utf8; do sleep 1; done
      cat /var/shared/qrcode.utf8
    fi
  '';
  formatConfigs.install-iso = {
    isoImage.squashfsCompression = "zstd -Xcompression-level 1";
  };
}
