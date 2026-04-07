{
  # Use this path to our repo root e.g. for UI test
  # inputs.clan-core.url = "../../../../.";

  # this placeholder is replaced by the path to nixpkgs
  inputs.clan-core.url = "__CLAN_CORE__";
  inputs.nixpkgs.url = "__NIXPKGS__";

  outputs =
    {
      self,
      clan-core,
      ...
    }:
    let
      clan = clan-core.lib.clan {
        inherit self;
        meta.name = "test_flake_with_core";
        # Don't quote this will be replaced by the inventory expression
        # Not a string!
        inventory = __INVENTORY_EXPR__;
        machines = {
          vm1 =
            { config, ... }:
            {
              nixpkgs.hostPlatform = "x86_64-linux";
              clan.core.networking.targetHost = "__CLAN_TARGET_ADDRESS__";
              system.stateVersion = config.system.nixos.release;
              sops.age.keyFile = "__CLAN_SOPS_KEY_PATH__";
              clan.core.sops.defaultGroups = [ "admins" ];
              clan.virtualisation.graphics = false;

              clan.core.networking.zerotier._roles = [ "controller" ];
              networking.useDHCP = false;
            };
          vm2 =
            { config, ... }:
            {
              nixpkgs.hostPlatform = "x86_64-linux";
              imports = [ ];
              clan.core.networking.targetHost = "__CLAN_TARGET_ADDRESS__";
              system.stateVersion = config.system.nixos.release;
              sops.age.keyFile = "__CLAN_SOPS_KEY_PATH__";
              clan.core.networking.zerotier._roles = [ "peer" ];
            };
        };
      };
    in
    {
      clan = { };
      inherit (clan.config) nixosConfigurations nixosModules clanInternals;
    };
}
