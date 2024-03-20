{ self, ... }:
{
  flake.clanInternals =
    (self.lib.buildClan {
      clanName = "testclan";
      directory = ../..;
      machines.test-backup = {
        imports = [ self.nixosModules.test-backup ];
        fileSystems."/".device = "/dev/null";
        boot.loader.grub.device = "/dev/null";
      };
    }).clanInternals;
  flake.nixosModules = {

    test-backup =
      {
        pkgs,
        lib,
        config,
        ...
      }:
      let
        dependencies = [
          self
          pkgs.stdenv.drvPath
          self.clanInternals.machines.${pkgs.hostPlatform.system}.test-backup.config.system.clan.deployment.file
        ] ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs);
        closureInfo = pkgs.closureInfo { rootPaths = dependencies; };
      in
      {
        imports = [
          self.clanModules.borgbackup
          self.clanModules.sshd
        ];
        clan.networking.targetHost = "machine";
        networking.hostName = "machine";
        services.openssh.settings.UseDns = false;

        programs.ssh.knownHosts = {
          machine.hostNames = [ "machine" ];
          machine.publicKey = builtins.readFile ../lib/ssh/pubkey;
        };

        users.users.root.openssh.authorizedKeys.keyFiles = [ ../lib/ssh/pubkey ];

        systemd.tmpfiles.settings."vmsecrets" = {
          "/root/.ssh/id_ed25519" = {
            C.argument = "${../lib/ssh/privkey}";
            z = {
              mode = "0400";
              user = "root";
            };
          };
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
        clanCore.clanDir = ../..;

        environment.systemPackages = [ self.packages.${pkgs.system}.clan-cli ];
        environment.etc.install-closure.source = "${closureInfo}/store-paths";
        nix.settings = {
          substituters = lib.mkForce [ ];
          hashed-mirrors = null;
          connect-timeout = lib.mkForce 3;
          flake-registry = pkgs.writeText "flake-registry" ''{"flakes":[],"version":2}'';
        };
        system.extraDependencies = dependencies;
        clanCore.state.test-backups.folders = [ "/var/test-backups" ];
        clan.borgbackup.destinations.test-backup.repo = "borg@machine:.";

        services.borgbackup.repos.test-backups = {
          path = "/var/lib/borgbackup/test-backups";
          authorizedKeys = [ (builtins.readFile ../lib/ssh/pubkey) ];
        };
      };
  };
  perSystem =
    { nodes, pkgs, ... }:
    {
      checks = pkgs.lib.mkIf (pkgs.stdenv.isLinux) {
        test-backups = (import ../lib/test-base.nix) {
          name = "test-backups";
          nodes.machine.imports = [
            self.nixosModules.clanCore
            self.nixosModules.test-backup
          ];

          testScript = ''
            import json
            start_all()

            # dummy data
            machine.succeed("mkdir -p /var/test-backups")
            machine.succeed("echo testing > /var/test-backups/somefile")

            # create
            machine.succeed("clan --debug --flake ${self} backups create test-backup")
            machine.wait_until_succeeds("! systemctl is-active borgbackup-job-test-backup >&2")

            # list
            backup_id = json.loads(machine.succeed("borg-job-test-backup list --json"))["archives"][0]["archive"]
            out = machine.succeed("clan --debug --flake ${self} backups list test-backup")
            print(out)
            assert backup_id in out, f"backup {backup_id} not found in {out}"

            # restore
            machine.succeed("rm -f /var/test-backups/somefile")
            machine.succeed(f"clan --debug --flake ${self} backups restore test-backup borgbackup borg@machine:.::{backup_id} >&2")
            assert machine.succeed("cat /var/test-backups/somefile").strip() == "testing", "restore failed"
          '';
        } { inherit pkgs self; };
      };
    };
}
