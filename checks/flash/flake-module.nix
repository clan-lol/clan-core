{
  self,
  lib,
  ...
}@flakeModule:
let
  importFlake =
    flakeDir:
    let
      flakeExpr = import (flakeDir + "/flake.nix");
      inputs = lib.intersectAttrs flakeExpr.inputs self.inputs;
      flake = flakeExpr.outputs (
        inputs
        // {
          self = flake // {
            outPath = flakeDir;
          };
          clan-core = self;
          systems = builtins.toFile "flake.systems.nix" ''
            [ "x86_64-linux" "aarch64-linux" ]
          '';
        }
      );
    in
    lib.throwIf (lib.pathExists (
      flakeDir + "/flake.lock"
    )) "checks/flash/ must not have a flake.lock file" flake;

  testFlake = importFlake ./.;
in
{
  perSystem =
    {
      pkgs,
      ...
    }:
    let
      nixosConfig = testFlake.nixosConfigurations."test-flash-machine-${pkgs.stdenv.hostPlatform.system}";
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

      # Filtered clan-core source used as the `clan-core` input of the flash
      # child flake when we lock it for offline use inside the VM. Using a
      # whitelist (`include`) keeps this source hash stable against irrelevant
      # changes at the repo root so checks/dont-depend-on-repo-root.nix stays
      # green.
      clan-core-flake-filtered = self.filter {
        name = "clan-core-flake-filtered";
        include = [
          "flake.nix"
          "flake.lock"
          "checks"
          "clanServices"
          "darwinModules"
          "flakeModules"
          "lib"
          "modules"
          "nixosModules"
        ];
      };

      systemsFile = builtins.toFile "flake.systems.nix" ''[ "${pkgs.stdenv.hostPlatform.system}" ]'';

      # Offline-locked copy of the flash child flake. This is what the VM
      # copies to `/flake` so that `clan flash write --flake /flake
      # test-flash-machine-${system}` can evaluate the child flake without any
      # network access. Mirrors the recipe used by lib/clanTest flakeForSandbox.
      flashTestFlake =
        pkgs.runCommand "flash-test-flake-${pkgs.stdenv.hostPlatform.system}"
          {
            nativeBuildInputs = [ pkgs.nix ];
          }
          ''
            cp -r ${./.} $out
            chmod +w -R $out
            export HOME=$(mktemp -d)
            nix flake lock $out \
              --extra-experimental-features 'nix-command flakes' \
              --override-input clan-core ${clan-core-flake-filtered} \
              --override-input nixpkgs ${self.inputs.nixpkgs} \
              --override-input systems 'path://${systemsFile}' \
              --override-input clan-core/nixpkgs ${self.inputs.nixpkgs} \
              --override-input clan-core/flake-parts ${self.inputs.flake-parts} \
              --override-input clan-core/treefmt-nix ${self.inputs.treefmt-nix} \
              --override-input clan-core/nix-select ${self.inputs.nix-select} \
              --override-input clan-core/data-mesher ${self.inputs.data-mesher} \
              --override-input clan-core/sops-nix ${self.inputs.sops-nix} \
              --override-input clan-core/disko ${self.inputs.disko} \
              --override-input clan-core/systems ${self.inputs.systems}
          '';

      dependencies = [
        pkgs.disko
        pkgs.buildPackages.lndir
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
        nixosConfig.pkgs.gnupg
        nixosConfig.pkgs.gnupg.src
        nixosConfig.pkgs.libselinux
        nixosConfig.pkgs.libselinux.src

        flashTestFlake
      ]
      ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs)
      ++ builtins.map (import ./facter-report.nix) (
        lib.filter (lib.hasSuffix "linux") flakeModule.config.systems
      );
      closureInfo = pkgs.closureInfo { rootPaths = dependencies; };
    in
    {
      # Skip flash test on aarch64-linux for now as it's too slow
      checks =
        lib.optionalAttrs
          (pkgs.stdenv.hostPlatform.isLinux && pkgs.stdenv.hostPlatform.system != "aarch64-linux")
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
                flake_dir = "${flashTestFlake}"
                machine.succeed("echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIRWUusawhlIorx7VFeQJHmMkhl9X3QpnvOdhnV/bQNG root@target' > ./test_id_ed25519.pub")
                # Some distros like to automount disks with spaces
                machine.succeed('mkdir -p "/mnt/with spaces" && mkfs.ext4 /dev/vdc && mount /dev/vdc "/mnt/with spaces"')
                machine.succeed(f"cp -r {flake_dir} /flake")
                machine.succeed("chmod -R +w /flake")
                machine.succeed("clan vars keygen --flake /flake </dev/null")
                machine.succeed("clan flash write --ssh-pubkey ./test_id_ed25519.pub --keymap de --language de_DE.UTF-8 --debug --flake /flake --yes --disk main /dev/vdc test-flash-machine-${pkgs.stdenv.hostPlatform.system}")
              '';
            } { inherit pkgs self; };
          };
    };
}
