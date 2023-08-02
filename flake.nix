{
  description = "clan.lol base operating system";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    disko.url = "github:nix-community/disko";
    disko.inputs.nixpkgs.follows = "nixpkgs";
    nixos-generators.url = "github:nix-community/nixos-generators";
    nixos-generators.inputs.nixpkgs.follows = "nixpkgs";
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
    pre-commit-hooks-nix.url = "github:cachix/pre-commit-hooks.nix";
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
        ./flake-parts/installer.nix
        ./flake-parts/tea-create-pr
        ./flake-parts/writers
        ./templates/flake-module.nix
        ./templates/python-project/flake-module.nix
        ./pkgs/clan-cli/flake-module.nix
        ./lib/flake-module.nix
      ];
    });
}
