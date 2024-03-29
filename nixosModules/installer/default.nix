{
  lib,
  pkgs,
  modulesPath,
  ...
}:
{
  systemd.tmpfiles.rules = [ "d /var/shared 0777 root root - -" ];
  imports = [
    (modulesPath + "/profiles/installation-device.nix")
    (modulesPath + "/profiles/all-hardware.nix")
    (modulesPath + "/profiles/base.nix")
  ];
  services.openssh.settings.PermitRootLogin = "yes";
  system.activationScripts.root-password = ''
    mkdir -p /var/shared
    ${pkgs.pwgen}/bin/pwgen -s 16 1 > /var/shared/root-password
    echo "root:$(cat /var/shared/root-password)" | chpasswd
  '';
  hidden-ssh-announce = {
    enable = true;
    script = pkgs.writeShellScript "write-hostname" ''
      set -efu
      export PATH=${
        lib.makeBinPath (
          with pkgs;
          [
            iproute2
            coreutils
            jq
            qrencode
          ]
        )
      }

      mkdir -p /var/shared
      echo "$1" > /var/shared/onion-hostname
      local_addrs=$(ip -json addr | jq '[map(.addr_info) | flatten | .[] | select(.scope == "global") | .local]')
      jq -nc \
        --arg password "$(cat /var/shared/root-password)" \
        --arg onion_address "$(cat /var/shared/onion-hostname)" \
        --argjson local_addrs "$local_addrs" \
        '{ password: $password, onion_address: $onion_address, local_addresses: $local_addrs }' \
        > /var/shared/login.json
      cat /var/shared/login.json | qrencode -t utf8 -o /var/shared/qrcode.utf8
    '';
  };
  services.getty.autologinUser = lib.mkForce "root";
  programs.bash.interactiveShellInit = ''
    if [[ "$(tty)" =~ /dev/(tty1|hvc0|ttyS0)$ ]]; then
      echo -n 'waiting for tor to generate the hidden service'
      until test -e /var/shared/qrcode.utf8; do echo -n .; sleep 1; done
      echo
      echo "Root password: $(cat /var/shared/root-password)"
      echo "Onion address: $(cat /var/shared/onion-hostname)"
      echo "Local network addresses:"
      ${pkgs.iproute}/bin/ip -brief -color addr | grep -v 127.0.0.1
      cat /var/shared/qrcode.utf8
    fi
  '';

  boot.loader.systemd-boot.enable = true;

  # Grub doesn't find devices for both BIOS and UEFI?

  #boot.loader.grub.efiInstallAsRemovable = true;
  #boot.loader.grub.efiSupport = true;
  disko.devices = {
    disk = {
      stick = {
        type = "disk";
        device = "/vda";
        imageSize = "3G";
        content = {
          type = "gpt";
          partitions = {
            #boot = {
            #  size = "1M";
            #  type = "EF02"; # for grub MBR
            #};
            ESP = {
              size = "100M";
              type = "EF00";
              content = {
                type = "filesystem";
                format = "vfat";
                mountpoint = "/boot";
              };
            };
            root = {
              size = "100%";
              content = {
                type = "filesystem";
                format = "ext4";
                mountpoint = "/";
              };
            };
          };
        };
      };
    };
  };
}
