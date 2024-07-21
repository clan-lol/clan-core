{
  description = "<Put your description here>";

  inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";

  outputs =
    { self, clan-core, ... }:
    let
      # Usage see: https://docs.clan.lol
      clan = clan-core.lib.buildClan {
        directory = self;
        # Ensure this is unique among all clans you want to use.
        meta.name = "__CHANGE_ME__";

        # Prerequisite: boot into the installer
        # See: https://docs.clan.lol/getting-started/installer
        # local> mkdir -p ./machines/machine1
        # local> Edit ./machines/<machine>/configuration.nix to your liking
        machines = {
          # "jon" will be the hostname of the machine
          jon = {
            imports = [ ./machines/jon/configuration.nix ];
          };
          # "sara" will be the hostname of the machine
          sara = {
            imports = [ ./machines/sara/configuration.nix ];
          };
        };
      };
    in
    {
      # all machines managed by Clan
      inherit (clan) nixosConfigurations clanInternals;
      # add the Clan cli tool to the dev shell
      # use the "nix develop" command to enter the dev shell
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
