{ ... }: {
  imports = [
    ./clan-cli/flake-module.nix
    ./clan-vm-manager/flake-module.nix
    ./installer/flake-module.nix
    ./ui/flake-module.nix
    ./theme/flake-module.nix
  ];

  perSystem = { pkgs, config, ... }: {
    packages = {
      tea-create-pr = pkgs.callPackage ./tea-create-pr { };
      zerotier-members = pkgs.callPackage ./zerotier-members { };
      merge-after-ci = pkgs.callPackage ./merge-after-ci {
        inherit (config.packages) tea-create-pr;
      };
      pending-reviews = pkgs.callPackage ./pending-reviews { };
      nix-unit = pkgs.callPackage ./nix-unit { };
      meshname = pkgs.callPackage ./meshname { };
      inherit (pkgs.callPackages ./node-packages { }) prettier-plugin-tailwindcss;
    };
  };
}
