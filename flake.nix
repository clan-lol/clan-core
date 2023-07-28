{
  description = "clan.lol base operating system";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixos-generators.url = "github:nix-community/nixos-generators";
    nixos-generators.inputs.nixpkgs.follows = "nixpkgs";
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = inputs @ { flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } ({ ... }: {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      imports = [
        ./flake-parts/devShells
        ./flake-parts/formatting.nix
        ./flake-parts/merge-after-ci
        ./flake-parts/modules.nix
        ./flake-parts/packages.nix
        ./flake-parts/tea-create-pr
        ./flake-parts/writers
        ./templates/flake-module.nix
        ./templates/python-project/flake-module.nix
        ./pkgs/clan-cli/flake-module.nix
      ];
      flake = {
        nixosModules = {
          installer = {
            imports = [
              ./modules/installer.nix
              ./modules/hidden-ssh-announce.nix
            ];
          };
          hidden-announce = {
            imports = [
              ./modules/hidden-ssh-announce.nix
            ];
          };
        };
      };
    });
}
