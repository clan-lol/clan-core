{
  description = "clan.lol base operating system";

  nixConfig.extra-substituters = [ "https://cache.clan.lol" ];
  nixConfig.extra-trusted-public-keys = [
    "cache.clan.lol-1:3KztgSAB5R1M+Dz7vzkBGzXdodizbgLXGXKXlcQLA28="
  ];

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable-small";
    disko.url = "github:nix-community/disko";
    disko.inputs.nixpkgs.follows = "nixpkgs";
    sops-nix.url = "github:Mic92/sops-nix";
    sops-nix.inputs.nixpkgs.follows = "nixpkgs";
    sops-nix.inputs.nixpkgs-stable.follows = "";
    nixos-generators.url = "github:nix-community/nixos-generators";
    nixos-generators.inputs.nixpkgs.follows = "nixpkgs";
    nixos-images.url = "github:nix-community/nixos-images";
    nixos-images.inputs.nixos-unstable.follows = "nixpkgs";
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    inputs@{ flake-parts, self, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (
      { ... }:
      {
        clan = {
          # meta.name = "clan-core";
          directory = self;
        };
        systems = [
          "x86_64-linux"
          "aarch64-linux"
          "aarch64-darwin"
        ];
        imports = [
          ./checks/flake-module.nix
          ./clanModules/flake-module.nix
          ./flakeModules/flake-module.nix
          (import ./flakeModules/clan.nix inputs.self)
          ./devShell.nix
          # TODO: migrate this @davHau
          # ./docs/flake-module
          ./docs/nix/flake-module.nix
          ./formatter.nix
          ./lib/flake-module.nix
          ./nixosModules/flake-module.nix
          ./pkgs/flake-module.nix
          ./templates/flake-module.nix
        ];
      }
    );
}
