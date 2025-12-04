{
  config,
  self,
  lib,
  ...
}:
{
  clan.machines = lib.listToAttrs (
    lib.map (
      system:
      lib.nameValuePair "test-flash-machine-${system}" {
        clan.core.networking.targetHost = "test-flash-machine";
        fileSystems."/".device = lib.mkDefault "/dev/vda";
        boot.loader.grub.device = lib.mkDefault "/dev/vda";

        # We need to use `mkForce` because we inherit from `test-install-machine`
        # which currently hardcodes `nixpkgs.hostPlatform`
        nixpkgs.hostPlatform = lib.mkForce system;

        imports = [ self.nixosModules.test-flash-machine ];
      }
    ) (lib.filter (lib.hasSuffix "linux") config.systems)
  );

  flake.nixosModules = {
    test-flash-machine =
      { lib, ... }:
      {
        imports = [ self.nixosModules.test-install-machine-without-system ];

        # We don't want our system to define any `vars` generators as these can't
        # be generated as the flake is inside `/nix/store`.
        clan.core.settings.state-version.enable = false;
        clan.core.vars.generators.test = lib.mkForce { };
        disko.devices.disk.main.preCreateHook = lib.mkForce "";

        # Every option here should match the options set through `clan flash write`
        # if you get a mass rebuild on the disko derivation, this means you need to
        # adjust something here. Also make sure that the injected json in clan flash write
        # is up to date.
        i18n.defaultLocale = "de_DE.UTF-8";
        console.keyMap = "de";
        services.xserver.xkb.layout = "de";
        users.users.root.openssh.authorizedKeys.keys = [
          "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIRWUusawhlIorx7VFeQJHmMkhl9X3QpnvOdhnV/bQNG root@target\n"
        ];
      };

  };

  perSystem =
    {
      pkgs,
      lib,
      ...
    }:
    let
      dependencies = [
        pkgs.disko
        pkgs.buildPackages.xorg.lndir
        pkgs.glibcLocales
        pkgs.kbd.out
        self.nixosConfigurations."test-flash-machine-${pkgs.stdenv.hostPlatform.system}".pkgs.perlPackages.ConfigIniFiles
        self.nixosConfigurations."test-flash-machine-${pkgs.stdenv.hostPlatform.system}".pkgs.perlPackages.FileSlurp
        pkgs.bubblewrap

        self.nixosConfigurations."test-flash-machine-${pkgs.stdenv.hostPlatform.system}".config.system.build.toplevel
        self.nixosConfigurations."test-flash-machine-${pkgs.stdenv.hostPlatform.system}".config.system.build.diskoScript
        self.nixosConfigurations."test-flash-machine-${pkgs.stdenv.hostPlatform.system}".config.system.build.diskoScript.drvPath
      ]
      ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs)
      ++ builtins.map (import ../installation/facter-report.nix) (
        lib.filter (lib.hasSuffix "linux") config.systems
      );
      closureInfo = pkgs.closureInfo { rootPaths = dependencies; };
    in
    {
      # Skip flash test on aarch64-linux for now as it's too slow
      checks =
        lib.optionalAttrs (pkgs.stdenv.isLinux && pkgs.stdenv.hostPlatform.system != "aarch64-linux")
          {
            nixos-test-flash = self.clanLib.test.baseTest {
              name = "flash";
              nodes.target = {
                virtualisation.emptyDiskImages = [ 4096 ];
                virtualisation.memorySize = 4096;

                virtualisation.useNixStoreImage = true;
                virtualisation.writableStore = true;

                environment.systemPackages = [ self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli ];
                environment.etc."install-closure".source = "${closureInfo}/store-paths";

                nix.settings = {
                  substituters = lib.mkForce [ ];
                  hashed-mirrors = null;
                  connect-timeout = lib.mkForce 3;
                  flake-registry = "";
                  experimental-features = [
                    "nix-command"
                    "flakes"
                  ];
                };
              };
              testScript = ''
                start_all()
                machine.succeed("echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIRWUusawhlIorx7VFeQJHmMkhl9X3QpnvOdhnV/bQNG root@target' > ./test_id_ed25519.pub")
                # Some distros like to automount disks with spaces
                machine.succeed('mkdir -p "/mnt/with spaces" && mkfs.ext4 /dev/vdc && mount /dev/vdc "/mnt/with spaces"')
                machine.succeed("clan flash write --ssh-pubkey ./test_id_ed25519.pub --keymap de --language de_DE.UTF-8 --debug --flake ${
                  self.packages.${pkgs.stdenv.buildPlatform.system}.clan-core-flake
                } --yes --disk main /dev/vdc test-flash-machine-${pkgs.stdenv.hostPlatform.system}")
              '';
            } { inherit pkgs self; };
          };
    };
}
