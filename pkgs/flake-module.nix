{ ... }: {
  imports = [
    ./clan-cli/flake-module.nix
    ./installer/flake-module.nix
    ./ui/flake-module.nix
  ];

  perSystem = { pkgs, config, ... }: {
    packages = {
      tea-create-pr = pkgs.callPackage ./tea-create-pr { };
      merge-after-ci = pkgs.callPackage ./merge-after-ci {
        inherit (config.packages) tea-create-pr;
      };
      nix-unit = pkgs.callPackage ./nix-unit { };
    };
  };
}
