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
        # We need to use `mkForce` because we inherit from `test-install-machine`
        # which currently hardcodes `nixpkgs.hostPlatform`
        nixpkgs.hostPlatform = lib.mkForce system;

        imports = [
          self.nixosModules.test-flash-machine
        ];
      }
    ) (lib.filter (lib.hasSuffix "linux") config.systems)
  );

  flake.nixosModules = {
    test-flash-machine =
      { lib, ... }:
      {
        imports = [ self.nixosModules.test-install-machine-without-system ];

        clan.core.networking.targetHost = "test-flash-machine";
        fileSystems."/".device = lib.mkDefault "/dev/vda";
        boot.loader.grub.device = lib.mkDefault "/dev/vda";

        # We don't want our system to define any `vars` generators as these can't
        # be generated as the flake is inside `/nix/store`.
        clan.core.settings.state-version.enable = false;
        clan.core.vars.generators.test-partitioning = lib.mkForce { };
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
      nixosConfig = self.nixosConfigurations."test-flash-machine-${pkgs.stdenv.hostPlatform.system}";
      #extraSystemConfigJSON = ''{"i18n": {"defaultLocale": "de_DE.UTF-8"}, "console": {"keyMap": "de"}, "services": {"xserver": {"xkb": {"layout": "de"}}}, "users": {"users": {"root": {"openssh": {"authorizedKeys": {"keys": ["ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIRWUusawhlIorx7VFeQJHmMkhl9X3QpnvOdhnV/bQNG root@target\n"]}}}}}}'';
      extraSystemConfig = {
        i18n.defaultLocale = "de_DE.UTF-8";
        console.keyMap = "de";
        services.xserver.xkb.layout = "de";
        users.users.root.openssh.authorizedKeys.keys = [
          "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIRWUusawhlIorx7VFeQJHmMkhl9X3QpnvOdhnV/bQNG root@target\n"
        ];
      };
      /*
        disko injects configuration, which we need to imitate here, so the correct paths are cached
        For reference, disko-cli.nix is called like this
        nix-build /nix/store/y8i903kl17890zs32pqgj30b4h5bl19a-disko-1.12.0/share/disko/install-cli.nix \
          --extra-experimental-features 'nix-command flakes' \
          --option no-write-lock-file true --option dry-run true --no-out-link --impure \
          --argstr flake /flake \
          --argstr flakeAttr test-flash-machine-x86_64-linux \
          --argstr rootMountPoint /mnt/disko-install-root \
          --arg writeEfiBootEntries false \
          --arg diskMappings '{ "main" = "/dev/vdc"; }' \
          --argstr extraSystemConfig '{"i18n": {"defaultLocale": "de_DE.UTF-8"}, "console": {"keyMap": "de"}, "services": {"xserver": {"xkb": {"layout": "de"}}}, "users": {"users": {"root": {"openssh": {"authorizedKeys": {"keys": ["ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIRWUusawhlIorx7VFeQJHmMkhl9X3QpnvOdhnV/bQNG root@target\n"]}}}}}}' -A installToplevel -A closureInfo -A diskoScript
      */
      installSystem = nixosConfig.extendModules {
        modules = [
          extraSystemConfig
          (
            { lib, ... }:
            {
              boot.loader.efi.canTouchEfiVariables = lib.mkVMOverride false;
              boot.loader.grub.devices = lib.mkVMOverride [ "/dev/vdc" ];
            }
          )
        ];
      };
      installSystemClosureInfo = installSystem.pkgs.closureInfo {
        rootPaths = [ installSystem.config.system.build.toplevel ];
      };
      dependencies = [
        pkgs.disko
        pkgs.buildPackages.xorg.lndir
        pkgs.glibcLocales
        pkgs.kbd.out
        nixosConfig.pkgs.perlPackages.ConfigIniFiles
        nixosConfig.pkgs.perlPackages.FileSlurp
        pkgs.bubblewrap

        # Include the full system closure to ensure all dependencies are available
        nixosConfig.config.system.build.toplevel
        nixosConfig.config.system.build.diskoScript

        installSystem.config.system.build.toplevel
        installSystem.config.system.build.diskoScript
        pkgs.stdenv.drvPath
        pkgs.bash.drvPath
        installSystemClosureInfo

        # Include openssh and its dependencies with source tarballs to avoid fetching during installation
        nixosConfig.pkgs.openssh
        nixosConfig.pkgs.openssh.src
        nixosConfig.pkgs.ldns
        nixosConfig.pkgs.ldns.src
        nixosConfig.pkgs.softhsm
        nixosConfig.pkgs.softhsm.src
        nixosConfig.pkgs.libredirect
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
              extraPythonPackages = _p: [
                self.legacyPackages.${pkgs.stdenv.hostPlatform.system}.nixosTestLib
              ];
              nodes.target = {
                virtualisation.emptyDiskImages = [ 4096 ];
                virtualisation.memorySize = 4096;

                virtualisation.useNixStoreImage = true;
                virtualisation.writableStore = true;

                environment.systemPackages = [
                  self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full
                ];
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
              # The clan flash command has to be ran inside a VM, as in the driver sandbox
              #   we cannot setup loop devices for the mount
              testScript = ''
                start_all()
                flake_dir = "${self.packages.${pkgs.stdenv.buildPlatform.system}.clan-core-flake}"
                machine.succeed("echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIRWUusawhlIorx7VFeQJHmMkhl9X3QpnvOdhnV/bQNG root@target' > ./test_id_ed25519.pub")
                # Some distros like to automount disks with spaces
                machine.succeed('mkdir -p "/mnt/with spaces" && mkfs.ext4 /dev/vdc && mount /dev/vdc "/mnt/with spaces"')
                machine.succeed(f"cp -r {flake_dir} /flake")
                machine.succeed("clan vars keygen --flake /flake </dev/null")
                machine.succeed("clan flash write --ssh-pubkey ./test_id_ed25519.pub --keymap de --language de_DE.UTF-8 --debug --flake /flake --yes --disk main /dev/vdc test-flash-machine-${pkgs.stdenv.hostPlatform.system}")
              '';
            } { inherit pkgs self; };
          };
    };
}
