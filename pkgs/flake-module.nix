{ inputs, ... }:

{
  imports = [
    ./clan-cli/flake-module.nix
    ./ui/clan-app/flake-module.nix
    ./clan-vm-manager/flake-module.nix
    ./installer/flake-module.nix
    ./ui/webview-ui/flake-module.nix
    ./distro-packages/flake-module.nix
    ./icon-update/flake-module.nix
    ./generate-test-vars/flake-module.nix
    ./clan-core-flake/flake-module.nix
  ];

  flake.packages.x86_64-linux =
    let
      pkgs = inputs.nixpkgs.legacyPackages.x86_64-linux;
    in
    {
      yagna = pkgs.callPackage ./yagna { };
    };

  perSystem =
    { config, pkgs, ... }:
    {
      packages = {
        tea-create-pr = pkgs.callPackage ./tea-create-pr { };
        zerotier-members = pkgs.callPackage ./zerotier-members { };
        zt-tcp-relay = pkgs.callPackage ./zt-tcp-relay { };
        moonlight-sunshine-accept = pkgs.callPackage ./moonlight-sunshine-accept { };
        merge-after-ci = pkgs.callPackage ./merge-after-ci { inherit (config.packages) tea-create-pr; };
        minifakeroot = pkgs.callPackage ./minifakeroot { };
        pending-reviews = pkgs.callPackage ./pending-reviews { };
        editor = pkgs.callPackage ./editor/clan-edit-codium.nix { };
        classgen = pkgs.callPackage ./classgen { };
        zerotierone = pkgs.callPackage ./zerotierone { };
        webview-lib = pkgs.callPackage ./ui/webview-lib { };
        update-clan-core-for-checks = pkgs.callPackage ./update-clan-core-for-checks { };
      };
    };
}
