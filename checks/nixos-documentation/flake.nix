{
  inputs.clan-core.url = "https://__replace__";
  inputs.nixpkgs.url = "https://__replace__";
  inputs.clan-core.inputs.nixpkgs.follows = "nixpkgs";
  inputs.systems.url = "https://__systems__";
  inputs.systems.flake = false;

  outputs =
    {
      self,
      clan-core,
      systems,
      ...
    }:
    let
      clan = clan-core.lib.clan {
        inherit self;

        machines.test-documentation =
          { lib, ... }:
          {
            nixpkgs.hostPlatform = lib.head (import systems);

            # Dummy file system
            fileSystems."/".device = "/dev/null";
            fileSystems."/".fsType = "ext4";
            boot.loader.grub.device = "/dev/null";

            # This is how some downstream users currently generate documentation
            # If this breaks notify them via matrix since we spent ~5 hrs for bughunting last time.
            documentation.nixos.enable = true;
            documentation.nixos.extraModules = [
              clan-core.nixosModules.clanCore
              {
                clan.core.settings.directory = ./.;
                # clanConfig is normally injected by clan-core.lib.clan into each machine,
                # but documentation.nixos.extraModules runs a separate NixOS eval where
                # it is not available. Provide a stub so the readOnly option is satisfied.
                clanConfig.vars.settings = { };
              }
            ];
          };

        inventory =
          { ... }:
          {
            meta.name = "test-documentation";
            meta.domain = "test-documentation";
            machines.test-documentation = { };
          };
      };
    in
    {
      inherit (clan.config) nixosConfigurations nixosModules clanInternals;
    };
}
