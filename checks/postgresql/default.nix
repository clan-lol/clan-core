(import ../lib/container-test.nix) (
  {
    name = "postgresql";

    nodes.machine = { self, ... }:
      {
        imports = [
          self.nixosModules.clanCore
          self.clanModules.postgresql
          self.clanModules.localbackup
        ];
        clan.postgresl.databases.test = {};
        clan.localbackup.targets.hdd.directory = "/mnt/external-disk";
      };
    testScript = ''
      start_all()
      machine.succeed("systemctl status postgresql")
      machine.wait_for_unit("postgresql")
      machine.succeed("/run/current-system/sw/bin/localbackup-create >&2")
      machine.succeed("ls -la /var/backups/postgresql")
    '';
})
