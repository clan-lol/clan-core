{
  description = "";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
    nixpkgs.url = "nixpkgs/nixos-unstable";
  };

  outputs = inputs @ { flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {

      systems = builtins.fromJSON (builtins.readFile ./systems.json);

      imports =
        let
          relPaths = builtins.fromJSON (builtins.readFile ./imports.json);
          paths = map (path: ./. + path) relPaths;
        in
        paths;
    };
}
