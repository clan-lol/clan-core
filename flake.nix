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
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (
      { lib, ... }:
      {
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
          {
            options.flake = flake-parts.lib.mkSubmoduleOptions {
              clanInternals = lib.mkOption {
                type = lib.types.submodule {
                  options = {
                    all-machines-json = lib.mkOption { type = lib.types.attrsOf lib.types.str; };
                    machines = lib.mkOption { type = lib.types.attrsOf (lib.types.attrsOf lib.types.unspecified); };
                    machinesFunc = lib.mkOption { type = lib.types.attrsOf (lib.types.attrsOf lib.types.unspecified); };
                  };
                };
              };
            };
          }
        ];
      }
    );
}
