{
  self,
  lib,
  ...
}:
let
  installer =
    { modulesPath, pkgs, ... }:
    let
      dependencies = [
        self
        self.clanInternals.machines.${pkgs.hostPlatform.system}.test-install-machine-with-system.config.system.build.toplevel
        self.clanInternals.machines.${pkgs.hostPlatform.system}.test-install-machine-with-system.config.system.build.diskoScript
        self.clanInternals.machines.${pkgs.hostPlatform.system}.test-install-machine-with-system.config.system.clan.deployment.file
        pkgs.stdenv.drvPath
        pkgs.bash.drvPath
        pkgs.nixos-anywhere
        pkgs.bubblewrap
      ] ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs);
      closureInfo = pkgs.closureInfo { rootPaths = dependencies; };
    in
    {
      imports = [
        (modulesPath + "/../tests/common/auto-format-root-device.nix")
      ];
      networking.useNetworkd = true;
      services.openssh.enable = true;
      services.openssh.settings.UseDns = false;
      services.openssh.settings.PasswordAuthentication = false;
      system.nixos.variant_id = "installer";
      environment.systemPackages = [
        self.packages.${pkgs.system}.clan-cli-full
        pkgs.nixos-facter
      ];
      environment.etc."install-closure".source = "${closureInfo}/store-paths";
      virtualisation.emptyDiskImages = [ 512 ];
      virtualisation.diskSize = 8 * 1024;
      virtualisation.rootDevice = "/dev/vdb";
      # both installer and target need to use the same diskImage
      virtualisation.diskImage = "./target.qcow2";
      virtualisation.memorySize = 3048;
      nix.settings = {
        substituters = lib.mkForce [ ];
        hashed-mirrors = null;
        connect-timeout = lib.mkForce 3;
        flake-registry = pkgs.writeText "flake-registry" ''{"flakes":[],"version":2}'';
        experimental-features = [
          "nix-command"
          "flakes"
        ];
      };
      users.users.nonrootuser = {
        isNormalUser = true;
        openssh.authorizedKeys.keyFiles = [ ../lib/ssh/pubkey ];
        extraGroups = [ "wheel" ];
      };
      security.sudo.wheelNeedsPassword = false;
      system.extraDependencies = dependencies;
    };
in
{

  # The purpose of this test is to ensure `clan machines install` works
  # for machines that don't have a hardware config yet.

  # If this test starts failing it could be due to the `facter.json` being out of date
  # you can get a new one by adding
  # client.fail("cat test-flake/machines/test-install-machine/facter.json >&2")
  # to the installation test.
  clan.machines.test-install-machine-without-system = {
    fileSystems."/".device = lib.mkDefault "/dev/vda";
    boot.loader.grub.device = lib.mkDefault "/dev/vda";

    imports = [ self.nixosModules.test-install-machine-without-system ];
  };
  clan.machines.test-install-machine-with-system =
    { pkgs, ... }:
    {
      # https://git.clan.lol/clan/test-fixtures
      facter.reportPath = builtins.fetchurl {
        url = "https://git.clan.lol/clan/test-fixtures/raw/commit/4a2bc56d886578124b05060d3fb7eddc38c019f8/nixos-vm-facter-json/${pkgs.hostPlatform.system}.json";
        sha256 =
          {
            aarch64-linux = "sha256:1rlfymk03rmfkm2qgrc8l5kj5i20srx79n1y1h4nzlpwaz0j7hh2";
            x86_64-linux = "sha256:16myh0ll2gdwsiwkjw5ba4dl23ppwbsanxx214863j7nvzx42pws";
          }
          .${pkgs.hostPlatform.system};
      };

      fileSystems."/".device = lib.mkDefault "/dev/vda";
      boot.loader.grub.device = lib.mkDefault "/dev/vda";

      imports = [ self.nixosModules.test-install-machine-without-system ];
    };
  flake.nixosModules = {
    test-install-machine-without-system =
      { lib, modulesPath, ... }:
      {
        imports = [
          (modulesPath + "/testing/test-instrumentation.nix") # we need these 2 modules always to be able to run the tests
          (modulesPath + "/profiles/qemu-guest.nix")
          ../lib/minify.nix
        ];

        networking.hostName = "test-install-machine";

        environment.etc."install-successful".text = "ok";

        boot.consoleLogLevel = lib.mkForce 100;
        boot.kernelParams = [ "boot.shell_on_fail" ];

        # disko config
        boot.loader.grub.efiSupport = lib.mkDefault true;
        boot.loader.grub.efiInstallAsRemovable = lib.mkDefault true;
        clan.core.vars.settings.secretStore = "vm";
        clan.core.vars.generators.test = {
          files.test.neededFor = "partitioning";
          script = ''
            echo "notok" > "$out"/test
          '';
        };
        disko.devices = {
          disk = {
            main = {
              type = "disk";
              device = "/dev/vda";

              preCreateHook = ''
                test -e /run/partitioning-secrets/test/test
              '';

              content = {
                type = "gpt";
                partitions = {
                  boot = {
                    size = "1M";
                    type = "EF02"; # for grub MBR
                    priority = 1;
                  };
                  ESP = {
                    size = "512M";
                    type = "EF00";
                    content = {
                      type = "filesystem";
                      format = "vfat";
                      mountpoint = "/boot";
                      mountOptions = [ "umask=0077" ];
                    };
                  };
                  root = {
                    size = "100%";
                    content = {
                      type = "filesystem";
                      format = "ext4";
                      mountpoint = "/";
                    };
                  };
                };
              };
            };
          };
        };
      };
  };

  perSystem =
    {
      pkgs,
      ...
    }:
    {
      # On aarch64-linux, hangs on reboot with after installation:
      # vm-test-run-test-installation-> installer # [  288.002871] reboot: Restarting system
      # vm-test-run-test-installation-> server # [test-install-machine] ### Done! ###
      # vm-test-run-test-installation-> server # [test-install-machine] + step 'Done!'
      # vm-test-run-test-installation-> server # [test-install-machine] + echo '### Done! ###'
      # vm-test-run-test-installation-> server # [test-install-machine] + rm -rf /tmp/tmp.qb16EAq7hJ
      # vm-test-run-test-installation-> (finished: must succeed: clan machines install --debug --flake test-flake --yes test-install-machine --target-host root@installer --update-hardware-config nixos-facter >&2, in 154.62 seconds)
      # vm-test-run-test-installation-> target: starting vm
      # vm-test-run-test-installation-> target: QEMU running (pid 144)
      # vm-test-run-test-installation-> target: waiting for unit multi-user.target
      # vm-test-run-test-installation-> target: waiting for the VM to finish booting
      # vm-test-run-test-installation-> target: Guest root shell did not produce any data yet...
      # vm-test-run-test-installation-> target:   To debug, enter the VM and run 'systemctl status backdoor.service'.
      checks = pkgs.lib.mkIf (pkgs.stdenv.isLinux && !pkgs.stdenv.isAarch64) {
        installation = (import ../lib/test-base.nix) {
          name = "installation";
          nodes.target = {
            services.openssh.enable = true;
            virtualisation.diskImage = "./target.qcow2";
            virtualisation.useBootLoader = true;
          };
          nodes.installer = installer;

          testScript = ''
            installer.start()

            installer.succeed("${pkgs.coreutils}/bin/install -Dm 600 ${../lib/ssh/privkey} /root/.ssh/id_ed25519")

            installer.wait_until_succeeds("timeout 2 ssh -o StrictHostKeyChecking=accept-new -v nonrootuser@localhost hostname")
            installer.succeed("cp -r ${../..} test-flake && chmod -R +w test-flake")

            installer.succeed("clan machines install --no-reboot --debug --flake test-flake --yes test-install-machine-without-system --target-host nonrootuser@localhost --update-hardware-config nixos-facter >&2")
            installer.shutdown()

            # We are missing the test instrumentation somehow. Test this later.
            target.state_dir = installer.state_dir
            target.start()
            target.wait_for_unit("multi-user.target")
          '';
        } { inherit pkgs self; };

        update-hardware-configuration = (import ../lib/test-base.nix) {
          name = "update-hardware-configuration";
          nodes.installer = installer;

          testScript = ''
            installer.start()
            installer.succeed("${pkgs.coreutils}/bin/install -Dm 600 ${../lib/ssh/privkey} /root/.ssh/id_ed25519")
            installer.wait_until_succeeds("timeout 2 ssh -o StrictHostKeyChecking=accept-new -v nonrootuser@localhost hostname")
            installer.succeed("cp -r ${../..} test-flake && chmod -R +w test-flake")
            installer.fail("test -f test-flake/machines/test-install-machine/hardware-configuration.nix")
            installer.fail("test -f test-flake/machines/test-install-machine/facter.json")

            installer.succeed("clan machines update-hardware-config --debug --flake test-flake test-install-machine-without-system nonrootuser@localhost >&2")
            installer.succeed("test -f test-flake/machines/test-install-machine-without-system/facter.json")
            installer.succeed("rm test-flake/machines/test-install-machine-without-system/facter.json")

            installer.succeed("clan machines update-hardware-config --debug --backend nixos-generate-config --flake test-flake test-install-machine-without-system nonrootuser@localhost >&2")
            installer.succeed("test -f test-flake/machines/test-install-machine-without-system/hardware-configuration.nix")
            installer.succeed("rm test-flake/machines/test-install-machine-without-system/hardware-configuration.nix")
          '';
        } { inherit pkgs self; };
      };
    };
}
