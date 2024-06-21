{
  # Use this path to our repo root e.g. for UI test
  # inputs.clan-core.url = "../../../../.";

  # this placeholder is replaced by the path to nixpkgs
  inputs.clan-core.url = "__CLAN_CORE__";

  outputs =
    { self, clan-core }:
    let
      clan = clan-core.lib.buildClan {
        directory = self;
        clanName = "test_flake_with_core";
        machines = {
          vm1 =
            { lib, ... }:
            {
              imports = [
                clan-core.clanModules.sshd
                clan-core.clanModules.root-password
              ];

              clan.networking.targetHost = "__CLAN_TARGET_ADDRESS__";
              system.stateVersion = lib.version;
              sops.age.keyFile = "__CLAN_SOPS_KEY_PATH__";
              clan.core.secretsUploadDirectory = "__CLAN_SOPS_KEY_DIR__";
              clan.core.sops.defaultGroups = [ "admins" ];
              clan.virtualisation.graphics = false;

              clan.networking.zerotier.controller.enable = true;
              networking.useDHCP = false;

              systemd.services.shutdown-after-boot = {
                enable = true;
                wantedBy = [ "multi-user.target" ];
                after = [ "multi-user.target" ];
                script = ''
                  #!/usr/bin/env bash
                  shutdown -h now
                '';
              };
            };
          vm2 =
            { lib, ... }:
            {
              imports = [
                clan-core.clanModules.sshd
                clan-core.clanModules.root-password
              ];
              clan.networking.targetHost = "__CLAN_TARGET_ADDRESS__";
              system.stateVersion = lib.version;
              sops.age.keyFile = "__CLAN_SOPS_KEY_PATH__";
              clan.core.secretsUploadDirectory = "__CLAN_SOPS_KEY_DIR__";
              clan.networking.zerotier.networkId = "82b44b162ec6c013";
            };
        };
      };
    in
    {
      inherit (clan) nixosConfigurations clanInternals;
    };
}
