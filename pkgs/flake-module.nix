{ inputs, ... }:

{
  imports = [
    ./clan-site/flake-module.nix
    ./network-status/flake-module.nix
    ./clan-cli/flake-module.nix
    ./clan-core-flake/flake-module.nix
    ./installer/flake-module.nix
    ./network-status/flake-module.nix
    ./docs-from-code/flake-module.nix
    ./testing/flake-module.nix
    ./clan-release-diff/flake-module.nix
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
        merge-after-ci = pkgs.callPackage ./merge-after-ci { inherit (config.packages) tea-create-pr; };
        pending-reviews = pkgs.callPackage ./pending-reviews { };
        datamodel-code-generator = pkgs.python3Packages.toPythonApplication (
          pkgs.python3Packages.callPackage ./datamodel-code-generator { }
        );
      }
      // lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
        editor = pkgs.callPackage ./editor/clan-edit-codium.nix { };
        disko = inputs.disko.packages.${pkgs.stdenv.hostPlatform.system}.disko;
      }
      // lib.optionalAttrs (pkgs.stdenv.hostPlatform.system == "x86_64-linux") {
        # The wrapper hardcodes legacyPackages.x86_64-linux.* flake refs, so the
        # tool is only meaningful on x86_64-linux; restricting registration keeps
        # it out of the all-packages aggregate on other systems.
        clan-release-diff = pkgs.callPackage ./clan-release-diff { };
      };
    };
}
