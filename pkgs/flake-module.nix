{ inputs, ... }:

{
  imports = [
    ./clan-app/flake-module.nix
    ./clan-site/flake-module.nix
    ./clan-cli/flake-module.nix
    ./clan-core-flake/flake-module.nix
    ./icon-update/flake-module.nix
    ./installer/flake-module.nix
    ./docs-from-code/flake-module.nix
    ./testing/flake-module.nix
  ];

  perSystem =
    {
      config,
      pkgs,
      lib,
      ...
    }:
    {
      packages = {
        tea-create-pr = pkgs.callPackage ./tea-create-pr { };
        zerotier-members = pkgs.callPackage ./zerotier-members { };
        merge-after-ci = pkgs.callPackage ./merge-after-ci { inherit (config.packages) tea-create-pr; };
        minifakeroot = pkgs.callPackage ./minifakeroot { };
        pending-reviews = pkgs.callPackage ./pending-reviews { };
        zerotierone = pkgs.callPackage ./zerotierone { };
        datamodel-code-generator = pkgs.python3Packages.toPythonApplication (
          pkgs.python3Packages.callPackage ./datamodel-code-generator { }
        );
      }
      // lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
        editor = pkgs.callPackage ./editor/clan-edit-codium.nix { };
        disko = inputs.disko.packages.${pkgs.stdenv.hostPlatform.system}.disko;
      };
    };
}
