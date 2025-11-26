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
        treefmt-nix.follows = "treefmt-nix";
      };
    };

  };

  outputs =
    inputs@{
      nixpkgs,
      systems,
      flake-parts,
      ...
    }:
    let
      inherit (nixpkgs.lib)
        filter
        optional
        pathExists
        ;

      privateInputs =
        if builtins.pathExists (./. + "/.skip-private-inputs") then
          { }
        else
          (import ./devFlake/flake-compat.nix {
            src = ./devFlake;
          }).outputs.inputs;
    in
    flake-parts.lib.mkFlake
      {
        inherit inputs;
        specialArgs = {
          inherit privateInputs;
        };
      }
      (
        { ... }:
        {
          debug = true;
          clan = {
            meta.name = "clan-core";
            inventory = {
              instances.internet.roles.default.tags = [ "all" ];
              machines = {
                "test-darwin-machine" = {
                  machineClass = "darwin";
                };
              };
            };
            # Allows downstream users to inject "unsupported" nixpkgs versions
            checks.minNixpkgsVersion.ignore = true;
          };
          systems = import systems;
          imports = [
            flake-parts.flakeModules.modules
          ]
          ++
            # only importing existing paths allows to minimize the flake for test
            # by removing files
            filter pathExists [
              ./checks/flake-module.nix
              ./clanModules/flake-module.nix
              ./clanServices/flake-module.nix
              ./devShell.nix
              ./docs/nix/flake-module.nix
              ./flakeModules/demo_iso.nix
              ./flakeModules/flake-module.nix
              ./lib/filter-clan-core/flake-module.nix
              ./lib/flake-module.nix
              ./lib/flake-parts/clan-nixos-test.nix
              ./modules/flake-module.nix
              ./nixosModules/clanCore/vars/flake-module.nix
              ./nixosModules/flake-module.nix
              ./pkgs/clan-cli/clan_cli/tests/flake-module.nix
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
