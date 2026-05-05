{
  ...
}:
let
  # Common target VM configuration used by both installation and update tests
  target =
    {
      lib,
      modulesPath,
      pkgs,
      ...
    }:
    {
      imports = [
        (modulesPath + "/../tests/common/auto-format-root-device.nix")
      ];

      networking.useNetworkd = true;
      services.openssh.enable = true;
      services.openssh.settings.UseDns = false;
      system.nixos.variant_id = "installer";
      environment.systemPackages = [
        # nixos-facter v0.4.3 aborts on ID_BUS values added by systemd
        # 260 (e.g. "acpi"); upstream fix is nix-community/nixos-facter#578.
        (pkgs.nixos-facter.overrideAttrs (old: {
          patches = (old.patches or [ ]) ++ [
            (pkgs.fetchpatch {
              name = "udev-drop-bus-field-dispatch-on-id_bus-string.patch";
              url = "https://github.com/nix-community/nixos-facter/pull/578/commits/e43c4459184a39ed6f3aa746a49170ae79d93bcd.patch";
              hash = "sha256-bm8CmUhRAlq8mLPgAwMS1akb/oN3qbW8JkypQ9Zed5M=";
            })
          ];
        }))
      ];
      # Disable cache.nixos.org to speed up tests
      nix.settings.substituters = lib.mkForce [ ];
      virtualisation.emptyDiskImages = [ 512 ];
      virtualisation.diskSize = 8 * 1024;
      virtualisation.rootDevice = "/dev/vdb";
      virtualisation.fileSystems."/".autoFormat = true;
      # both installer and target need to use the same diskImage
      virtualisation.diskImage = "./target.qcow2";
      virtualisation.memorySize = 3048;
      users.users.nonrootuser = {
        isNormalUser = true;
        openssh.authorizedKeys.keys = [ (builtins.readFile ../assets/ssh/pubkey) ];
        extraGroups = [ "wheel" ];
      };
      users.users.root.openssh.authorizedKeys.keys = [ (builtins.readFile ../assets/ssh/pubkey) ];
      # Allow users to manage their own SSH keys
      services.openssh.authorizedKeysFiles = [
        "/root/.ssh/authorized_keys"
        "/home/%u/.ssh/authorized_keys"
        "/etc/ssh/authorized_keys.d/%u"
      ];
      security.sudo.wheelNeedsPassword = false;
    };
in
{
  inherit
    target
    ;
}
