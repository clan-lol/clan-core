{
  description = "clan.lol base operating system";

  inputs = {
    nixpkgs.url = "https://nixos.org/channels/nixpkgs-unstable/nixexprs.tar.xz";

    nix-darwin.url = "github:nix-darwin/nix-darwin";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";

    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";

    disko.url = "github:nix-community/disko";
    disko.inputs.nixpkgs.follows = "nixpkgs";

    nixos-facter-modules.url = "github:nix-community/nixos-facter-modules";

    sops-nix.url = "github:Mic92/sops-nix";
    sops-nix.inputs.nixpkgs.follows = "nixpkgs";

    systems.url = "github:nix-systems/default";

    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";

    nix-select.url = "https://git.clan.lol/clan/nix-select/archive/main.tar.gz";

    data-mesher = {
      url = "https://git.clan.lol/clan/data-mesher/archive/main.tar.gz";
      inputs = {
        flake-parts.follows = "flake-parts";
        nixpkgs.follows = "nixpkgs";
        systems.follows = "systems";
        treefmt-nix.follows = "treefmt-nix";
      };
    };

    # dependencies needed for nuschtos
    flake-utils.url = "github:numtide/flake-utils";
    flake-utils.inputs.systems.follows = "systems";
    nuschtos.url = "github:NuschtOS/search";
    nuschtos.inputs.nixpkgs.follows = "nixpkgs";
    nuschtos.inputs.flake-utils.follows = "flake-utils";
  };

  outputs =
    inputs@{
      flake-parts,
      nixpkgs,
      systems,
      ...
    }:
    let
      inherit (nixpkgs.lib)
        filter
        optional
        pathExists
        ;
    in
    flake-parts.lib.mkFlake { inherit inputs; } (
      { ... }:
      {
        clan = {
          meta.name = "clan-core";
          inventory = {
            services = { };
            machines = {
              "test-darwin-machine" = {
                machineClass = "darwin";
              };
            };
          };
        };
        systems = import systems;
        imports =
          [ flake-parts.flakeModules.modules ]
          ++
            # only importing existing paths allows to minimize the flake for test
            # by removing files
            filter pathExists [
              ./checks/flake-module.nix
              ./clanModules/flake-module.nix
              ./clanServices/flake-module.nix
              ./devShell.nix
              ./docs/nix/flake-module.nix
              ./flakeModules/flake-module.nix
              ./flakeModules/demo_iso.nix
              ./lib/filter-clan-core/flake-module.nix
              ./lib/flake-module.nix
              ./lib/flake-parts/clan-nixos-test.nix
              ./nixosModules/clanCore/vars/flake-module.nix
              ./nixosModules/flake-module.nix
              ./pkgs/flake-module.nix
              ./templates/flake-module.nix
            ]
          ++ [
            (if pathExists ./flakeModules/clan.nix then import ./flakeModules/clan.nix inputs.self else { })
          ]
          # Make treefmt-nix optional
          # This only works if you set inputs.clan-core.inputs.treefmt-nix.follows
          # to a non-empty input that doesn't export a flakeModule
          ++ optional (pathExists ./formatter.nix && inputs.treefmt-nix ? flakeModule) ./formatter.nix;
      }
    );
}
