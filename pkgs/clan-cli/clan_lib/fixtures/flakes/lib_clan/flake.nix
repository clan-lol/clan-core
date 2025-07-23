{
  inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  inputs.nixpkgs.follows = "clan-core/nixpkgs";

  outputs =
    { self, clan-core, ... }:
    let
      clan = clan-core.lib.clan ({
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
