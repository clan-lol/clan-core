{
  inputs.clan-core.url = "__CLAN_CORE__";

  outputs =
    { self, clan-core }:
    let
      clan = clan-core.lib.clan {
        inherit self;
        meta.name = "test-flake";
        machines = {
          test-vm-persistence = {
            imports = [ clan-core.nixosModules.test-vm-persistence ];
            nixpkgs.hostPlatform = "__SYSTEM__";
          };
          test-vm-deployment = {
            imports = [ clan-core.nixosModules.test-vm-deployment ];
            nixpkgs.hostPlatform = "__SYSTEM__";
          };
        };
      };
    in
    {
      inherit (clan.config) nixosConfigurations;
      inherit (clan.config) nixosModules;
      inherit (clan.config) clanInternals;
      clan = clan.config;
    };
}
