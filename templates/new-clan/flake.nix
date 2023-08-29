{
  description = "<Put your description here>";

  inputs.clan-core.url = "git+https://git.clan.lol/clan/clan-core";

  outputs = { clan-core, ... }: {
    nixosConfigurations = clan-core.lib.buildClan {
      directory = ./.;
    };
  };
}
