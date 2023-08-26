{
  description = "<Put your description here>";

  inputs = {
    clan-core.url = "git+https://git.clan.lol/clan/clan-core";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = inputs @ { flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" ];
      imports = [
        ./clan-flake-module.nix
      ];
    };
}
