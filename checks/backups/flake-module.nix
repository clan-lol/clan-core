{ self, ... }:
{
  clan.machines.test-backup = {
    imports = [ self.nixosModules.test-backup ];
    fileSystems."/".device = "/dev/null";
    boot.loader.grub.device = "/dev/null";
  };
  clan.inventory.services = {
    borgbackup.test-backup = {
      roles.client.machines = [ "test-backup" ];
      roles.server.machines = [ "test-backup" ];
    };
  };
  flake.nixosModules = {
    test-backup =
      {
        pkgs,
        lib,
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
          # Do not import inventory modules. They should be configured via 'clan.inventory'
          #
          # TODO: Configure localbackup via inventory
          self.clanModules.localbackup
        ];
        # Borgbackup overrides
        services.borgbackup.repos.test-backups = {
          path = "/var/lib/borgbackup/test-backups";
          authorizedKeys = [ (builtins.readFile ../lib/ssh/pubkey) ];
        };
        clan.borgbackup.destinations.test-backup.repo = lib.mkForce "borg@machine:.";

        clan.core.networking.targetHost = "machine";
        networking.hostName = "machine";

        programs.ssh.knownHosts = {
          machine.hostNames = [ "machine" ];
          machine.publicKey = builtins.readFile ../lib/ssh/pubkey;
        };

        services.openssh = {
          enable = true;
          settings.UsePAM = false;
          settings.UseDns = false;
          hostKeys = [
            {
              path = "/root/.ssh/id_ed25519";
              type = "ed25519";
            }
          ];
        };

        users.users.root.openssh.authorizedKeys.keyFiles = [ ../lib/ssh/pubkey ];

        # This is needed to unlock the user for sshd
        # Because we use sshd without setuid binaries
        users.users.borg.initialPassword = "hello";

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
          "/etc/secrets/borgbackup/borgbackup.ssh" = {
            C.argument = "${../lib/ssh/privkey}";
            z = {
              mode = "0400";
              user = "root";
            };
          };
          "/etc/secrets/borgbackup/borgbackup.repokey" = {
            C.argument = builtins.toString (pkgs.writeText "repokey" "repokey12345");
            z = {
              mode = "0400";
              user = "root";
            };
          };
        };
        clan.core.facts.secretStore = "vm";
        clan.core.vars.settings.secretStore = "vm";

        environment.systemPackages = [ self.packages.${pkgs.system}.clan-cli ];
        environment.etc.install-closure.source = "${closureInfo}/store-paths";
        nix.settings = {
          substituters = lib.mkForce [ ];
          hashed-mirrors = null;
          connect-timeout = lib.mkForce 3;
          flake-registry = pkgs.writeText "flake-registry" ''{"flakes":[],"version":2}'';
        };
        system.extraDependencies = dependencies;
        clan.core.state.test-backups.folders = [ "/var/test-backups" ];

        clan.core.state.test-service = {
          preBackupScript = ''
            touch /var/test-service/pre-backup-command
          '';
          preRestoreScript = ''
            touch /var/test-service/pre-restore-command
          '';
          postRestoreScript = ''
            touch /var/test-service/post-restore-command
          '';
          folders = [ "/var/test-service" ];
        };

        fileSystems."/mnt/external-disk" = {
          device = "/dev/vdb"; # created in tests with virtualisation.emptyDisks
          autoFormat = true;
          fsType = "ext4";
          options = [
            "defaults"
            "noauto"
          ];
        };

        clan.localbackup.targets.hdd = {
          directory = "/mnt/external-disk";
          preMountHook = ''
            touch /run/mount-external-disk
          '';
          postUnmountHook = ''
            touch /run/unmount-external-disk
          '';
        };
      };
  };
  perSystem =
    { pkgs, ... }:
    let
      clanCore = self.filter {
        include = [
          "checks/backups"
          "checks/flake-module.nix"
          "clanModules/borgbackup"
          "clanModules/flake-module.nix"
          "clanModules/localbackup"
          "clanModules/packages"
          "clanModules/single-disk"
          "clanModules/zerotier"
          "flake.lock"
          "flakeModules"
          "inventory.json"
          "nixosModules"
          # Just include everything in 'lib'
          # If anything changes in /lib that may affect everything
          "lib"
        ];
      };
    in
    {
      checks = pkgs.lib.mkIf pkgs.stdenv.isLinux {
        backups = (import ../lib/container-test.nix) {
          name = "backups";
          nodes.machine = {
            imports =
              [
                self.nixosModules.clanCore
                # Some custom overrides for the backup tests
                self.nixosModules.test-backup
              ]
              ++
              # import the inventory generated nixosModules
              self.clanInternals.inventoryClass.machines.test-backup.machineImports;
            clan.core.settings.directory = ./.;
            environment.systemPackages = [
              (pkgs.writeShellScriptBin "foo" ''
                echo ${clanCore}
              '')
            ];
          };

          testScript = ''
            import json
            start_all()

            # dummy data
            machine.succeed("mkdir -p /var/test-backups /var/test-service")
            machine.succeed("echo testing > /var/test-backups/somefile")

            # create
            machine.succeed("clan backups create --debug --flake ${clanCore} test-backup")
            machine.wait_until_succeeds("! systemctl is-active borgbackup-job-test-backup >&2")
            machine.succeed("test -f /run/mount-external-disk")
            machine.succeed("test -f /run/unmount-external-disk")

            # list
            backup_id = json.loads(machine.succeed("borg-job-test-backup list --json"))["archives"][0]["archive"]
            out = machine.succeed("clan backups list --debug --flake ${clanCore} test-backup").strip()
            print(out)
            assert backup_id in out, f"backup {backup_id} not found in {out}"
            localbackup_id = "hdd::/mnt/external-disk/snapshot.0"
            assert localbackup_id in out, "localbackup not found in {out}"

            ## borgbackup restore
            machine.succeed("rm -f /var/test-backups/somefile")
            machine.succeed(f"clan backups restore --debug --flake ${clanCore} test-backup borgbackup 'test-backup::borg@machine:.::{backup_id}' >&2")
            assert machine.succeed("cat /var/test-backups/somefile").strip() == "testing", "restore failed"
            machine.succeed("test -f /var/test-service/pre-restore-command")
            machine.succeed("test -f /var/test-service/post-restore-command")
            machine.succeed("test -f /var/test-service/pre-backup-command")

            ## localbackup restore
            machine.succeed("rm -rf /var/test-backups/somefile /var/test-service/ && mkdir -p /var/test-service")
            machine.succeed(f"clan backups restore --debug --flake ${clanCore} test-backup localbackup '{localbackup_id}' >&2")
            assert machine.succeed("cat /var/test-backups/somefile").strip() == "testing", "restore failed"
            machine.succeed("test -f /var/test-service/pre-restore-command")
            machine.succeed("test -f /var/test-service/post-restore-command")
            machine.succeed("test -f /var/test-service/pre-backup-command")
          '';
        } { inherit pkgs self; };
      };
    };
}
