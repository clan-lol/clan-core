{
  description = "clan.lol base operating system";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixos-generators.url = "github:nix-community/nixos-generators";
    nixos-generators.inputs.nixpkgs.follows = "nixpkgs";
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } ({ lib, config, ... }: {
      systems = lib.systems.flakeExposed;
      flake = {
        nixosConfigurations.installer = lib.nixosSystem {
          system = "x86_64-linux";
          modules = [
            config.flake.nixosModules.installer
            inputs.nixos-generators.nixosModules.all-formats
          ];
        };
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
