{
  lib,
  pkgs,
  ...
}:
let
  # Common target VM configuration used by both installation and update tests
  target =
    { modulesPath, pkgs, ... }:
    {
      imports = [
        (modulesPath + "/../tests/common/auto-format-root-device.nix")
      ];

      networking.useNetworkd = true;
      services.openssh.enable = true;
      services.openssh.settings.UseDns = false;
      system.nixos.variant_id = "installer";
      environment.systemPackages = [
        pkgs.nixos-facter
      ];
      # Disable cache.nixos.org to speed up tests
      nix.settings.substituters = [ ];
      nix.settings.trusted-public-keys = [ ];
      virtualisation.emptyDiskImages = [ 512 ];
      virtualisation.diskSize = 8 * 1024;
      virtualisation.rootDevice = "/dev/vdb";
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

  # NixOS test library combining port utils and clan VM test utilities
  nixosTestLib = pkgs.python3Packages.buildPythonPackage {
    pname = "nixos-test-lib";
    version = "1.0.0";
    format = "pyproject";
    src = lib.fileset.toSource {
      root = ./.;
      fileset = lib.fileset.unions [
        ./pyproject.toml
        ./nixos_test_lib
      ];
    };
    nativeBuildInputs = with pkgs.python3Packages; [
      setuptools
      wheel
    ];
    doCheck = false;
  };
in
{
  inherit
    target
    nixosTestLib
    ;
}
