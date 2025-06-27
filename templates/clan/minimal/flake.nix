{
  inputs = {
    clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
    nixpkgs.follows = "clan-core/nixpkgs";

    flake-parts.follows = "clan-core/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "clan-core/nixpkgs";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (
      { self, lib, ... }:
      {

        imports = [
          inputs.clan-core.flakeModules.default
        ];

        clan = {
          inherit self;
          specialArgs = { inherit inputs; };
          # Ensure this is unique among all clans you want to use.
          meta.name = lib.mkDefault "__CHANGE_ME__";
        };

        systems = [
          "x86_64-linux"
          "aarch64-linux"
          "x86_64-darwin"
          "aarch64-darwin"
        ];
      }
    );
}
