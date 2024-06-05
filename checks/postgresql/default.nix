(import ../lib/container-test.nix) ({
  name = "postgresql";

  nodes.machine =
    { self, config, ... }:
    {
      imports = [
        self.nixosModules.clanCore
        self.clanModules.postgresql
        self.clanModules.localbackup
      ];
      clan.postgresql.users.test = { };
      clan.postgresql.databases.test.create.options.OWNER = "test";
      clan.localbackup.targets.hdd.directory = "/mnt/external-disk";

      environment.systemPackages = [ config.services.postgresql.package ];
    };
  testScript =
    { nodes, ... }:
    ''
      start_all()
      machine.wait_for_unit("postgresql")
      # Create a test table
      machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -c 'CREATE TABLE test (id serial PRIMARY KEY);' test")

      machine.succeed("/run/current-system/sw/bin/localbackup-create >&2")

      machine.succeed("test -e /mnt/external-disk/snapshot.0/machine/var/backup/postgres/test/dump.sql.zstd || { echo 'dump.sql.zstd not found'; exit 1; }")
      machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -d test -c 'INSERT INTO test DEFAULT VALUES;'")
      machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -d test -c 'DROP TABLE test;'")
      machine.succeed("test -e /var/backup/postgres/test/dump.sql.zstd || { echo 'backup.info not found'; exit 1; }")

      machine.succeed("rm -rf /var/backup/postgres")

      machine.succeed("NAME=/mnt/external-disk/snapshot.0 FOLDERS=/var/backup/postgres/test /run/current-system/sw/bin/localbackup-restore >&2")
      machine.succeed("test -e /var/backup/postgres/test/dump.sql.zstd || { echo 'backup.info not found'; exit 1; }")

      machine.succeed("""
      set -x
      ${nodes.machine.clanCore.state.postgresql-test.postRestoreCommand}
      """)
      machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -l >&2")
      machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -d test -c '\dt' >&2")

      # Check that the table is still there
      machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -d test -c 'SELECT * FROM test;'")
      output = machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql --csv -c \"SELECT datdba::regrole FROM pg_database WHERE datname = 'test'\"")
      owner = output.split("\n")[1]
      assert owner == "test", f"Expected database owner to be 'test', got '{owner}'"
    '';
})
