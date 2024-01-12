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
      meshname = pkgs.callPackage ./meshname { };
    } // lib.optionalAttrs pkgs.stdenv.isLinux {
      wayland-proxy-virtwl = pkgs.callPackage ./wayland-proxy-virtwl { };
    };
  };
}
