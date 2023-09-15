{
  # this placeholder is replaced by the path to nixpkgs
  inputs.clan-core.url = "__CLAN_CORE__";

  outputs = { self, clan-core }: {
    nixosConfigurations = clan-core.lib.buildClan {
      directory = self;
      machines = {
        vm1 = { modulesPath, ... }: {
          imports = [ "${toString modulesPath}/virtualisation/qemu-vm.nix" ];
        };
      };
    };
  };
}
