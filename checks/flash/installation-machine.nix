{ clan-core }:
{ lib, modulesPath, ... }:
{
  imports = [
    (modulesPath + "/testing/test-instrumentation.nix")
    (modulesPath + "/profiles/qemu-guest.nix")
    clan-core.clanLib.test.minifyModule
  ];

  # Disable system.checks to avoid rebuild mismatches in tests
  system.checks = lib.mkForce [ ];

  # Default fs and bootloader
  fileSystems."/".device = lib.mkDefault "/dev/vda";
  fileSystems."/".fsType = lib.mkDefault "ext4";
  boot.loader.grub.device = lib.mkDefault "/dev/vda";

  networking.hostName = "test-install-machine";

  environment.etc."install-successful".text = "ok";

  # Enable SSH and add authorized key for testing.
  services.openssh.enable = true;
  services.openssh.settings.PasswordAuthentication = false;
  users.users.nonrootuser = {
    isNormalUser = true;
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBIbwIVnLy+uoDZ6uK/OCc1QK46SIGeC3mVc85dqLYQw lass@ignavia"
    ];
    extraGroups = [ "wheel" ];
    home = "/home/nonrootuser";
    createHome = true;
  };
  users.users.root.openssh.authorizedKeys.keys = [
    "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBIbwIVnLy+uoDZ6uK/OCc1QK46SIGeC3mVc85dqLYQw lass@ignavia"
  ];
  services.openssh.authorizedKeysFiles = [
    "/root/.ssh/authorized_keys"
    "/home/%u/.ssh/authorized_keys"
    "/etc/ssh/authorized_keys.d/%u"
  ];
  security.sudo.wheelNeedsPassword = false;

  boot.consoleLogLevel = lib.mkForce 100;
  boot.kernelParams = [ "boot.shell_on_fail" ];

  # disko config
  boot.loader.grub.efiSupport = lib.mkDefault true;
  boot.loader.grub.efiInstallAsRemovable = lib.mkDefault true;
  clan.core.vars.settings.secretStore = "sops";
  clan.core.vars.generators.test-partitioning = {
    files.test.neededFor = "partitioning";
    script = ''
      echo "notok" > "$out"/test
    '';
  };
  clan.core.vars.generators.test-activation = {
    files.test.neededFor = "activation";
    script = ''
      echo "almöhi" > "$out"/test
    '';
  };
  # an activation script that requires the activation secret to be present
  system.activationScripts.test-vars-activation.text = ''
    test -e /var/lib/sops-nix/activation/test-activation/test || {
      echo "\nTEST ERROR: Activation secret not found!\n" >&2
      exit 1
    }
  '';
  disko.devices = {
    disk = {
      main = {
        type = "disk";
        device = "/dev/vda";

        preCreateHook = ''
          test -e /run/partitioning-secrets/test-partitioning/test
        '';

        content = {
          type = "gpt";
          partitions = {
            boot = {
              size = "1M";
              type = "EF02"; # for grub MBR
              priority = 1;
            };
            ESP = {
              size = "512M";
              type = "EF00";
              content = {
                type = "filesystem";
                format = "vfat";
                mountpoint = "/boot";
                mountOptions = [ "umask=0077" ];
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
