{
  description = "clan.lol base operating system";

  nixConfig.extra-substituters = [ "https://cache.clan.lol" ];
  nixConfig.extra-trusted-public-keys = [ "cache.clan.lol-1:3KztgSAB5R1M+Dz7vzkBGzXdodizbgLXGXKXlcQLA28=" ];

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable-small";
    #nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable-small";
    # https://github.com/NixOS/nixpkgs/pull/265872
    nixpkgs-for-deal.url = "github:Luis-Hebendanz/nixpkgs/fix_python_deal";

    disko.url = "github:nix-community/disko";
    disko.inputs.nixpkgs.follows = "nixpkgs";
    sops-nix.url = "github:Mic92/sops-nix";
    sops-nix.inputs.nixpkgs.follows = "nixpkgs";
    sops-nix.inputs.nixpkgs-stable.follows = "";
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
      ];
      imports = [
        ./checks/flake-module.nix
        ./devShell.nix
        ./formatter.nix
        ./templates/flake-module.nix
        ./clanModules/flake-module.nix

        ./pkgs/flake-module.nix

        ./lib/flake-module.nix
        ./nixosModules/flake-module.nix
      ];
    });
}
