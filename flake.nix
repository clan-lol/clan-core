{
  description = "clan.lol base operating system";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    floco.url = "github:aakropotkin/floco";
    floco.inputs.nixpkgs.follows = "nixpkgs";
    disko.url = "github:nix-community/disko";
    disko.inputs.nixpkgs.follows = "nixpkgs";
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
        ./devShell.nix
        ./formatter.nix
        ./templates/flake-module.nix

        ./pkgs/flake-module.nix

        ./lib/flake-module.nix
        ({ self, lib, ... }: {
          flake.nixosModules = lib.mapAttrs (_: nix: { imports = [ nix ]; }) (self.lib.findNixFiles ./nixosModules);
          flake.clanModules = lib.mapAttrs (_: nix: { imports = [ nix ]; }) (self.lib.findNixFiles ./clanModules);
        })
      ];
    });
}
