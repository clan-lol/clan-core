{ self, ... }:
let
  clan = self.lib.buildClan {
    clanName = "testclan";
    directory = ../..;
    machines.test-backup = {
      imports = [ self.nixosModules.test-backup ];
      fileSystems."/".device = "/dev/null";
      boot.loader.grub.device = "/dev/null";
    };
  };
in
{
  flake.clanInternals = clan.clanInternals;
  flake.nixosModules = {
    test-backup = { pkgs, lib, config, ... }:
      let
        dependencies = [
          self
          pkgs.stdenv.drvPath
          clan.clanInternals.machines.x86_64-linux.test-backup.config.system.clan.deployment.file
        ] ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs);
        closureInfo = pkgs.closureInfo { rootPaths = dependencies; };
      in
      {
        imports = [
          self.clanModules.borgbackup
          self.clanModules.sshd
        ];
        clan.networking.targetHost = "test-backup";

        services.borgbackup.repos.testrepo = {
          authorizedKeys = [
            (builtins.readFile ../lib/ssh/pubkey)
          ];
        };

        networking.hostName = "client";
        services.sshd.enable = true;

        programs.ssh.knownHosts = {
          machine.hostNames = [ "machine" ];
          machine.publicKey = builtins.readFile ../lib/ssh/pubkey;
        };

        users.users.root.openssh.authorizedKeys.keyFiles = [
          ../lib/ssh/pubkey
        ];

        systemd.tmpfiles.settings."vmsecrets" = {
          "/etc/secrets/ssh.id_ed25519" = {
            C.argument = "${../lib/ssh/privkey}";
            z = {
              mode = "0400";
              user = "root";
            };
          };
          "/etc/secrets/borgbackup.ssh" = {
            C.argument = "${../lib/ssh/privkey}";
            z = {
              mode = "0400";
              user = "root";
            };
          };
          "/etc/secrets/borgbackup.repokey" = {
            C.argument = builtins.toString (pkgs.writeText "repokey" "repokey12345");
            z = {
              mode = "0400";
              user = "root";
            };
          };
        };
        clanCore.secretStore = "vm";

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
        clan.borgbackup.destinations.test-backup.repo = "borg@machine:.";
      };
  };
  perSystem = { nodes, pkgs, ... }: {
    checks = pkgs.lib.mkIf (pkgs.stdenv.isLinux) {
      test-backups =
        (import ../lib/test-base.nix)
          {
            name = "test-backups";
            nodes.machine.imports = [
              self.nixosModules.clanCore
              self.nixosModules.test-backup
              { clanCore.clanDir = ../..; }
            ];

            testScript = ''
              import json
              start_all()

              # dummy data
              client.succeed("mkdir /var/test-backups")
              client.succeed("echo testing > /var/test-backups/somefile")

              # create
              client.succeed("clan --debug --flake ${self} backups create test-backup")
              client.wait_until_succeeds("! systemctl is-active borgbackup-job-test-backup")

              # list
              backup_id = json.loads(client.succeed("borg-job-test-backup list --json"))["archives"][0]["archive"]
              assert(backup_id in client.succeed("clan --debug --flake ${self} backups list test-backup"))

              # restore
              client.succeed("rm -f /var/test-backups/somefile")
              client.succeed(f"clan --debug --flake ${self} backups restore test-backup borgbackup {backup_id}")
              assert(client.succeed("cat /var/test-backups/somefile").strip() == "testing")
            '';
          }
          { inherit pkgs self; };
    };
  };
}
