{ ... }:
{
  imports = [
    ./clan-cli/flake-module.nix
    ./clan-vm-manager/flake-module.nix
    ./installer/flake-module.nix
  ];

  perSystem =
    {
      pkgs,
      config,
      lib,
      ...
    }:
    {
      packages =
        {
          tea-create-pr = pkgs.callPackage ./tea-create-pr { };
          zerotier-members = pkgs.callPackage ./zerotier-members { };
          zt-tcp-relay = pkgs.callPackage ./zt-tcp-relay { };
          moonlight-sunshine-accept = pkgs.callPackage ./moonlight-sunshine-accept { };
          merge-after-ci = pkgs.callPackage ./merge-after-ci { inherit (config.packages) tea-create-pr; };
          pending-reviews = pkgs.callPackage ./pending-reviews { };
        }
        // lib.optionalAttrs pkgs.stdenv.isLinux {
          wayland-proxy-virtwl = pkgs.callPackage ./wayland-proxy-virtwl { };
          waypipe = pkgs.waypipe.overrideAttrs (_old: {
            # https://gitlab.freedesktop.org/mstoeckl/waypipe
            src = pkgs.fetchFromGitLab {
              domain = "gitlab.freedesktop.org";
              owner = "mstoeckl";
              repo = "waypipe";
              rev = "4e4ff3bc1943cf7f6aeb56b06c060f40578d3570";
              hash = "sha256-dxz4AmeJAweffyPCayvykworQNntHtHeq6PXMXWsM5k=";
            };
          });
          # halalify zerotierone
          zerotierone = pkgs.zerotierone.overrideAttrs (_old: {
            meta = _old.meta // {
              license = lib.licenses.apsl20;
            };
          });
        };
    };
}
