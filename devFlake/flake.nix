{
  description = "private dev inputs";

  # Dev dependencies
  inputs.nixpkgs-dev.url = "github:NixOS/nixpkgs/nixos-unstable-small";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.flake-utils.inputs.systems.follows = "systems";

  inputs.treefmt-nix.url = "github:numtide/treefmt-nix";
  inputs.treefmt-nix.inputs.nixpkgs.follows = "";

  inputs.systems.url = "github:nix-systems/default";

  inputs.test-fixtures.url = "git+https://git.clan.lol/clan/test-fixtures";
  inputs.test-fixtures.inputs.nixpkgs.follows = "nixpkgs-dev";

  outputs = inputs: inputs;
}
