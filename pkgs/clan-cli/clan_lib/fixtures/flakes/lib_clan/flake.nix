{
  inputs.Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  inputs.nixpkgs.follows = "Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU/nixpkgs";

  outputs =
    { self, Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU, ... }:
    let
      clan = Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU.lib.clan ({
        inherit self;
        imports = [
          ./clan.nix

          (builtins.fromJSON (builtins.readFile ./clan.json))

          (
            { lib, ... }:
            {
              meta.name = lib.mkDefault "_somename_";
            }
          )
        ];
      });
    in
    {
      clan = clan.config;
      inherit (clan.config) nixosConfigurations nixosModules clanInternals;
    };
}
