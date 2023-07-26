{
  description = "<Put your description here>";

  inputs = {
    clan-core.url = "git+https://git.clan.lol/clan/clan-core";
    flake-parts.url = "github:hercules-ci/flake-parts";
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
