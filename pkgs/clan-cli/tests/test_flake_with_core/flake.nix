{
  # Use this path to our repo root e.g. for UI test
  # inputs.clan-core.url = "../../../../.";

  # this placeholder is replaced by the path to nixpkgs
  inputs.clan-core.url = "__CLAN_CORE__";

  outputs = { self, clan-core }:
    let
      clan = clan-core.lib.buildClan {
        directory = self;
        machines = {
          vm1 = { lib, ... }: {
            clan.networking.deploymentAddress = "__CLAN_DEPLOYMENT_ADDRESS__";
            system.stateVersion = lib.version;
            sops.age.keyFile = "__CLAN_SOPS_KEY_PATH__";

            clan.networking.zerotier.controller.enable = true;

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
        };
      };
    in
    {
      inherit (clan) nixosConfigurations clanInternals;
    };
}
