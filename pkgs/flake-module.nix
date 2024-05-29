{ ... }:

{
  imports = [
    ./clan-cli/flake-module.nix
    ./clan-vm-manager/flake-module.nix
    ./installer/flake-module.nix
    ./schemas/flake-module.nix
    ./webview-ui/flake-module.nix
    ./gui-installer/flake-module.nix
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
          editor = pkgs.callPackage ./editor/clan-edit-codium.nix { };
        }
        // lib.optionalAttrs pkgs.stdenv.isLinux {
          # halalify zerotierone
          zerotierone = pkgs.zerotierone.overrideAttrs (_old: {
            meta = _old.meta // {
              license = lib.licenses.apsl20;
            };
          });
        };
    };
}
