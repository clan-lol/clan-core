{ ... }:

{
  imports = [
    ./clan-app/flake-module.nix
    ./clan-cli/flake-module.nix
    ./clan-core-flake/flake-module.nix
    ./clan-vm-manager/flake-module.nix
    ./icon-update/flake-module.nix
    ./installer/flake-module.nix
    ./option-search/flake-module.nix
    ./testing/flake-module.nix
  ];

  perSystem =
    { config, pkgs, ... }:
    {
      packages = {
        tea-create-pr = pkgs.callPackage ./tea-create-pr { };
        zerotier-members = pkgs.callPackage ./zerotier-members { };
        merge-after-ci = pkgs.callPackage ./merge-after-ci { inherit (config.packages) tea-create-pr; };
        minifakeroot = pkgs.callPackage ./minifakeroot { };
        pending-reviews = pkgs.callPackage ./pending-reviews { };
        editor = pkgs.callPackage ./editor/clan-edit-codium.nix { };
        classgen = pkgs.callPackage ./classgen { };
        zerotierone = pkgs.callPackage ./zerotierone { };
      };
    };
}
