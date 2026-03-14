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
      inherit (clan-core.inputs.nixpkgs) lib;

      hostSystem = lib.head (import systems);

      # Usage see: https://docs.clan.lol
      clan = clan-core.lib.clan {
        inherit self;

        machines.peer1 =
          { modulesPath, ... }:
          {
            nixpkgs.hostPlatform = hostSystem;

            imports = [
              # Required for the NixOS test driver backdoor (hvc0 shell)
              "${modulesPath}/testing/test-instrumentation.nix"
            ];

            # Fast squashfs compression for test speed
            image.modules.iso.isoImage.squashfsCompression = "zstd -Xcompression-level 1";

            # Minimize ISOLINUX boot menu delay (0 means infinite in syslinux)
            boot.loader.timeout = lib.mkForce 1;

            # Disable vars state version generation
            clan.core.settings.state-version.enable = true;

            # Enable one secret to be generated
            clan.core.vars.generators.test-generator = {
              files.test-secret.secret = true;
              script = "echo HongKong > $out/test-secret";
            };

            # Enable SSH for boot verification
            services.openssh.enable = true;
            services.openssh.settings.PermitRootLogin = "yes";
            users.users.root.openssh.authorizedKeys.keys = [
              (builtins.readFile (clan-core + "/checks/assets/ssh/pubkey"))
            ];
          };

        inventory =
          { ... }:
          {
            meta.name = "foo";
            meta.domain = "foo";
            machines.peer1 = { };
          };
      };
    in
    {
      # all machines managed by Clan
      inherit (clan.config) nixosConfigurations nixosModules clanInternals;
    };
}
