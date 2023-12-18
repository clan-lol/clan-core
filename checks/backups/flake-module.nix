{ self, ... }:
let
  clan = self.lib.buildClan {
    clanName = "testclan";
    directory = ../..;
    machines = {
      test_backup_client = {
        imports = [ self.nixosModules.test_backup_client ];
        fileSystems."/".device = "/dev/null";
        boot.loader.grub.device = "/dev/null";
      };
    };
  };
in
{
  flake.nixosConfigurations = { inherit (clan.nixosConfigurations) test_backup_client; };
  flake.clanInternals.machines = clan.clanInternals.machines;
  flake.nixosModules = {
    test_backup_server = { ... }: {
      imports = [
        self.clanModules.borgbackup
      ];
      services.sshd.enable = true;
      services.borgbackup.repos.testrepo = {
        authorizedKeys = [
          (builtins.readFile ../lib/ssh/pubkey)
        ];
      };
    };
    test_backup_client = { pkgs, lib, ... }:
      let
        dependencies = [
          self
          pkgs.stdenv.drvPath
        ] ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs);
        closureInfo = pkgs.closureInfo { rootPaths = dependencies; };
      in
      {
        imports = [
          self.clanModules.borgbackup
        ];
        networking.hostName = "client";
        services.sshd.enable = true;
        users.users.root.openssh.authorizedKeys.keyFiles = [
          ../lib/ssh/pubkey
        ];
        environment.systemPackages = [ self.packages.${pkgs.system}.clan-cli ];
        environment.etc."install-closure".source = "${closureInfo}/store-paths";
        nix.settings = {
          substituters = lib.mkForce [ ];
          hashed-mirrors = null;
          connect-timeout = lib.mkForce 3;
          flake-registry = pkgs.writeText "flake-registry" ''{"flakes":[],"version":2}'';
        };
        system.extraDependencies = dependencies;
        clanCore.state.test-backups.folders = [ "/var/test-backups" ];
        clan.borgbackup = {
          enable = true;
          destinations.test_backup_server = {
            repo = "borg@server:.";
            rsh = "ssh -i /root/.ssh/id_ed25519 -o StrictHostKeyChecking=no";
          };
        };
      };
  };
  perSystem = { nodes, pkgs, ... }: {
    checks = pkgs.lib.mkIf (pkgs.stdenv.isLinux) {
      test-backups =
        (import ../lib/test-base.nix)
          {
            name = "test-backups";
            nodes.server = {
              imports = [
                self.nixosModules.test_backup_server
                self.nixosModules.clanCore
                {
                  clanCore.machineName = "server";
                  clanCore.clanDir = ../..;
                }
              ];
            };
            nodes.client = {
              imports = [
                self.nixosModules.test_backup_client
                self.nixosModules.clanCore
                {
                  clanCore.machineName = "client";
                  clanCore.clanDir = ../..;
                }
              ];
            };

            testScript = ''
              import json
              start_all()

              # setup
              client.succeed("mkdir -m 700 /root/.ssh")
              client.succeed(
                  "cat ${../lib/ssh/privkey} > /root/.ssh/id_ed25519"
              )
              client.succeed("chmod 600 /root/.ssh/id_ed25519")
              client.wait_for_unit("sshd", timeout=30)
              print(client.succeed("ssh -o StrictHostKeyChecking=accept-new -v root@client hostname"))

              # dummy data
              client.succeed("mkdir /var/test-backups")
              client.succeed("echo testing > /var/test-backups/somefile")

              # create
              client.succeed("clan --flake ${../..} backups create test_backup_client")
              client.wait_until_succeeds("! systemctl is-active borgbackup-job-test_backup_server")

              # list
              backup_id = json.loads(client.succeed("borg-job-test_backup_server list --json"))["archives"][0]["archive"]
              assert(backup_id in client.succeed("clan --flake ${../..} backups list test_backup_client"))

              # restore
              client.succeed("rm -f /var/test-backups/somefile")
              client.succeed(f"clan --flake ${../..} backups restore test_backup_client borgbackup {backup_id}")
              assert(client.succeed("cat /var/test-backups/somefile").strip() == "testing")
            '';
          }
          { inherit pkgs self; };
    };
  };
}
