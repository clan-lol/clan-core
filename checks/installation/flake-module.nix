{ self, ... }:
let
  clan = self.lib.buildClan {
    clanName = "testclan";
    directory = ../..;
    machines = {
      test_install_machine = {
        clan.networking.targetHost = "test_install_machine";
        imports = [ self.nixosModules.test_install_machine ];
      };
    };
  };
in
{
  flake.nixosConfigurations = {
    inherit (clan.nixosConfigurations) test_install_machine;
  };
  flake.clanInternals = clan.clanInternals;
  flake.nixosModules = {
    test_install_machine =
      { lib, modulesPath, ... }:
      {
        imports = [
          self.clanModules.diskLayouts
          (modulesPath + "/testing/test-instrumentation.nix") # we need these 2 modules always to be able to run the tests
          (modulesPath + "/profiles/qemu-guest.nix")
        ];
        clan.diskLayouts.singleDiskExt4.device = "/dev/vdb";

        environment.etc."install-successful".text = "ok";

        boot.consoleLogLevel = lib.mkForce 100;
        boot.kernelParams = [ "boot.shell_on_fail" ];
      };
  };
  perSystem =
    {
      nodes,
      pkgs,
      lib,
      ...
    }:
    let
      dependencies = [
        self
        pkgs.stdenv.drvPath
        clan.clanInternals.machines.x86_64-linux.test_install_machine.config.system.build.toplevel
        clan.clanInternals.machines.x86_64-linux.test_install_machine.config.system.build.diskoScript
        clan.clanInternals.machines.x86_64-linux.test_install_machine.config.system.clan.deployment.file
        pkgs.nixos-anywhere
      ] ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs);
      closureInfo = pkgs.closureInfo { rootPaths = dependencies; };
    in
    {
      checks = pkgs.lib.mkIf (pkgs.stdenv.isLinux) {
        test-installation = (import ../lib/test-base.nix) {
          name = "test-installation";
          nodes.target = {
            services.openssh.enable = true;
            users.users.root.openssh.authorizedKeys.keyFiles = [ ../lib/ssh/pubkey ];
            system.nixos.variant_id = "installer";
            virtualisation.emptyDiskImages = [ 4096 ];
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
          };
          nodes.client = {
            environment.systemPackages = [ self.packages.${pkgs.system}.clan-cli ];
            environment.etc."install-closure".source = "${closureInfo}/store-paths";
            virtualisation.memorySize = 2048;
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
            system.extraDependencies = dependencies;
          };

          testScript = ''
            def create_test_machine(oldmachine=None, args={}): # taken from <nixpkgs/nixos/tests/installer.nix>
                startCommand = "${pkgs.qemu_test}/bin/qemu-kvm"
                startCommand += " -cpu max -m 1024 -virtfs local,path=/nix/store,security_model=none,mount_tag=nix-store"
                startCommand += f' -drive file={oldmachine.state_dir}/empty0.qcow2,id=drive1,if=none,index=1,werror=report'
                startCommand += ' -device virtio-blk-pci,drive=drive1'
                machine = create_machine({
                  "startCommand": startCommand,
                } | args)
                driver.machines.append(machine)
                return machine

            start_all()

            client.succeed("${pkgs.coreutils}/bin/install -Dm 600 ${../lib/ssh/privkey} /root/.ssh/id_ed25519")
            client.wait_until_succeeds("ssh -o StrictHostKeyChecking=accept-new -v root@target hostname")

            client.succeed("clan --debug --flake ${../..} machines install --yes test_install_machine root@target >&2")
            try:
              target.shutdown()
            except BrokenPipeError:
              # qemu has already exited
              pass

            new_machine = create_test_machine(oldmachine=target, args={ "name": "new_machine" })
            assert(new_machine.succeed("cat /etc/install-successful").strip() == "ok")
          '';
        } { inherit pkgs self; };
      };
    };
}
