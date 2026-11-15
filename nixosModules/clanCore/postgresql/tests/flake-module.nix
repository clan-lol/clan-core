{ ... }:
{
  perSystem =
    { ... }:
    {
      clan.nixosTests.postgresql = {

        name = "service-postgresql";

        clan = {
          directory = ./.;

          machines.machine = {
            clan.core.postgresql.enable = true;
            clan.core.postgresql.users.test = { };
            clan.core.postgresql.databases.test.create.options.OWNER = "test";
            clan.core.settings.directory = ./.;
          };
        };

        testScript =
          let
            runpg = "runuser -u postgres -- /run/current-system/sw/bin/psql";
          in
          ''
            start_all()
            machine.wait_for_unit("postgresql")

            # Create a test table
            machine.succeed("${runpg} -c 'CREATE TABLE test (id serial PRIMARY KEY);' test")

            # Insert valuesn
            machine.succeed("${runpg} -d test -c 'INSERT INTO test DEFAULT VALUES;'")

            # Check that we can read them back
            machine.succeed("${runpg} -d test -c 'SELECT * FROM test;'")

            # A layout left behind by older versions is world-readable
            machine.succeed("install -d -m 0755 /var/backup/postgres/test")
            machine.succeed("install -m 0644 /dev/null /var/backup/postgres/test/pg-dump")

            machine.succeed("pre-backup-test")
            for path, expected in [
                ("/var/backup/postgres", "700 root root"),
                ("/var/backup/postgres/test", "700 root root"),
                ("/var/backup/postgres/test/pg-dump", "600 root root"),
            ]:
                actual = machine.succeed(f"stat -c '%a %U %G' {path}").strip()
                assert actual == expected, f"{path}: {actual} != {expected}"
            machine.fail("runuser -u nobody -- cat /var/backup/postgres/test/pg-dump")

            # A Borg restore can leave the parent directories root-only (#7621)
            machine.succeed("chmod 0700 /var/backup")
            machine.fail("runuser -u postgres -- cat /var/backup/postgres/test/pg-dump")

            # The restore brings back the dumped rows
            machine.succeed("${runpg} -d test -c 'INSERT INTO test DEFAULT VALUES;'")
            machine.succeed("postgres-db-restore-command-test")
            rows = machine.succeed("${runpg} -d test -At -c 'SELECT count(*) FROM test;'").strip()
            assert rows == "1", f"expected 1 row after restore, got {rows}"

            # Backup providers call the post-restore hook, here with no stopOnRestore services
            machine.succeed("${runpg} -d test -c 'INSERT INTO test DEFAULT VALUES;'")
            machine.succeed("post-restore-test")
            rows = machine.succeed("${runpg} -d test -At -c 'SELECT count(*) FROM test;'").strip()
            assert rows == "1", f"expected 1 row after post-restore hook, got {rows}"
          '';
      };
    };
}
