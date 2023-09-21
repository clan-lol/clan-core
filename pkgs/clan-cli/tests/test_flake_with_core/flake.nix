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
          vm1 = { modulesPath, ... }: {
            imports = [ "${toString modulesPath}/virtualisation/qemu-vm.nix" ];
            clan.networking.deploymentAddress = "__CLAN_DEPLOYMENT_ADDRESS__";
            sops.age.keyFile = "__CLAN_SOPS_KEY_PATH__";

            clanCore.secrets.testpassword = {
              generator = ''
                echo "secret1" > "$secrets/secret1"
                echo "fact1" > "$facts/fact1"
              '';
              secrets.secret1 = { };
              facts.fact1 = { };
            };
          };
        };
      };
    in
    {
      inherit (clan) nixosConfigurations clanInternals;
    };
}
