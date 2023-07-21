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
        "aarch64-darwin"
        "x86_64-darwin"
      ];
      imports = [
        ./flake-parts/packages.nix
        ./flake-parts/formatting.nix
        ./templates/flake-module.nix
        ./templates/python-project/flake-module.nix
        ./pkgs/clan-cli/flake-module.nix
      ];
      flake = {
        nixosModules = {
          installer = {
            imports = [
              ./installer.nix
              ./hidden-announce.nix
            ];
          };
          hidden-announce = {
            imports = [
              ./hidden-announce.nix
            ];
          };
        };
      };
    });
}
