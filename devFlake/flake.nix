{
  description = "private dev inputs";

  # Dev dependencies
  inputs.nixpkgs-dev.url = "github:NixOS/nixpkgs/nixos-unstable-small";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.flake-utils.inputs.systems.follows = "systems";

  inputs.nuschtos.url = "github:NuschtOS/search";
  inputs.nuschtos.inputs.nixpkgs.follows = "nixpkgs-dev";

  inputs.treefmt-nix.url = "github:numtide/treefmt-nix";
  inputs.treefmt-nix.inputs.nixpkgs.follows = "";

  inputs.systems.url = "github:nix-systems/default";

  outputs = inputs: inputs;
}
