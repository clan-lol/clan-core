{
  inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  inputs.nixpkgs.follows = "clan-core/nixpkgs";

  outputs =
    { self, clan-core, ... }:
    let
      # Usage see: https://docs.clan.lol
      clan = clan-core.clanLib.buildClan {
        inherit self;

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
    in
    {

      # Expose clan structures as flake outputs. clanInternals is needed for
      # the clan-cli. Exposing nixosConfigurations allows using `nixos-rebuild` as before.
      inherit (clan)
        nixosConfigurations
        nixosModules
        clanInternals
        darwinConfigurations
        darwinModules
        ;

      # Add the Clan cli tool to the dev shell.
      # Use "nix develop" to enter the dev shell.
      devShells =
        clan-core.inputs.nixpkgs.lib.genAttrs
          [
            "x86_64-linux"
            "aarch64-linux"
            "aarch64-darwin"
            "x86_64-darwin"
          ]
          (system: {
            default = clan-core.inputs.nixpkgs.legacyPackages.${system}.mkShell {
              packages = [ clan-core.packages.${system}.clan-cli ];
            };
          });
    };
}
