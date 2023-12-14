{ ... }: {
  imports = [
    ./clan-cli/flake-module.nix
    ./clan-vm-manager/flake-module.nix
    ./installer/flake-module.nix
  ];

  perSystem = { pkgs, config, lib, ... }: {
    packages = {
      tea-create-pr = pkgs.callPackage ./tea-create-pr { };
      zerotier-members = pkgs.callPackage ./zerotier-members { };
      merge-after-ci = pkgs.callPackage ./merge-after-ci {
        inherit (config.packages) tea-create-pr;
      };
      pending-reviews = pkgs.callPackage ./pending-reviews { };
      nix-unit = pkgs.callPackage ./nix-unit { };
      meshname = pkgs.callPackage ./meshname { };
    } // lib.optionalAttrs pkgs.stdenv.isLinux {
      aemu = pkgs.callPackage ./aemu { };
      gfxstream = pkgs.callPackage ./gfxstream {
        inherit (config.packages) aemu;
      };
      rutabaga-gfx-ffi = pkgs.callPackage ./rutabaga-gfx-ffi {
        inherit (config.packages) gfxstream aemu;
      };
      qemu-wayland = pkgs.callPackage ./qemu-wayland {
        inherit (config.packages) rutabaga-gfx-ffi;
      };
    };
  };
}
