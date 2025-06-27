{
  inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  inputs.nixpkgs.follows = "clan-core/nixpkgs";
  inputs.flake-parts.follows = "clan-core/flake-parts";
  inputs.flake-parts.inputs.nixpkgs-lib.follows = "clan-core/nixpkgs";

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      imports = [ inputs.clan-core.flakeModules.default ];
      # https://docs.clan.lol/guides/getting-started/flake-parts/
      clan = {

        # Ensure this is unique among all clans you want to use.
        meta.name = "__CHANGE_ME__";

        # Information about your machines. Machines under ./machines will be auto-imported.
        inventory.machines = {
          somemachine.tags = [ "desktop" ];
          somemachine.deploy.targetHost = "root@somemachine";
        };

        # Clan services to use. See https://docs.clan.lol/reference/clanServices
        inventory.instances = {

          admin = {
            module = {
              name = "admin";
              input = "clan";
            };
            roles.default.tags.all = { };
          };

          zerotier = {
            module = {
              name = "zerotier";
              input = "clan";
            };
            roles.peer.tags.all = { };
          };
        };

        # A mapping of machine names to their nixos configuration. Allows specifying
        # additional configuration.
        machines = {
          somemachine =
            { pkgs, ... }:
            {
              environment.systemPackages = with pkgs; [ asciinema ];
            };
        };
      };
      perSystem =
        { pkgs, inputs', ... }:
        {
          devShells.default = pkgs.mkShell { packages = [ inputs'.clan-core.packages.clan-cli ]; };
        };
    };
}
