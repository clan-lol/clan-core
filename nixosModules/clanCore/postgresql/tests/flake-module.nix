{ self, ... }:
{
  perSystem =
    { ... }:
    {
      clan.nixosTests.postgresql = {

        name = "service-postgresql";

        clan = {
          directory = ./.;

          # Workaround until we can use nodes.machine = { };
          modules."@clan/importer" = ../../../../clanServices/importer;

          inventory = {
            machines.machine = { };
            instances.importer = {
              module.name = "@clan/importer";
              module.input = "self";
              roles.default.tags.all = { };
              roles.default.extraModules = [
                {

                  imports = [
                    #   self.nixosModules.clanCore
                    self.clanModules.localbackup
                  ];

                  clan.core.postgresql.enable = true;
                  clan.core.postgresql.users.test = { };
                  clan.core.postgresql.databases.test.create.options.OWNER = "test";
                  clan.core.postgresql.databases.test.restore.stopOnRestore = [ "sample-service" ];
                  clan.localbackup.targets.hdd.directory = "/mnt/external-disk";
                  clan.core.settings.directory = ./.;

                  systemd.services.sample-service = {
                    wantedBy = [ "multi-user.target" ];
                    script = ''
                      while true; do
                        echo "Hello, world!"
                        sleep 5
                      done
                    '';
                  };

                }
              ];
            };
          };
        };

        # TODO: Broken. Use instead of importer after fixing.
        # nodes.machine = { };

        testScript =

          { nodes, ... }:

          ''
            start_all()
            machine.wait_for_unit("postgresql")
            machine.wait_for_unit("sample-service")
            # Create a test table
            machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -c 'CREATE TABLE test (id serial PRIMARY KEY);' test")

            machine.succeed("/run/current-system/sw/bin/localbackup-create >&2")
            timestamp_before = int(machine.succeed("systemctl show --property=ExecMainStartTimestampMonotonic sample-service | cut -d= -f2").strip())

            # import time
            # time.sleep(5400000)

            machine.succeed("test -e /mnt/external-disk/snapshot.0/machine/var/backup/postgres/test/pg-dump || { echo 'pg-dump not found'; exit 1; }")
            machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -d test -c 'INSERT INTO test DEFAULT VALUES;'")
            machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -d test -c 'DROP TABLE test;'")
            machine.succeed("test -e /var/backup/postgres/test/pg-dump || { echo 'pg-dump not found'; exit 1; }")

            machine.succeed("rm -rf /var/backup/postgres")

            machine.succeed("NAME=/mnt/external-disk/snapshot.0 FOLDERS=/var/backup/postgres/test /run/current-system/sw/bin/localbackup-restore >&2")
            machine.succeed("test -e /var/backup/postgres/test/pg-dump || { echo 'pg-dump not found'; exit 1; }")

            machine.succeed("""
            set -x
            ${nodes.machine.clan.core.state.test.postRestoreCommand}
            """)
            machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -l >&2")
            machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -d test -c '\dt' >&2")

            timestamp_after = int(machine.succeed("systemctl show --property=ExecMainStartTimestampMonotonic sample-service | cut -d= -f2").strip())
            assert timestamp_before < timestamp_after, f"{timestamp_before} >= {timestamp_after}: expected sample-service to be restarted after restore"

            # Check that the table is still there
            machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -d test -c 'SELECT * FROM test;'")
            output = machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql --csv -c \"SELECT datdba::regrole FROM pg_database WHERE datname = 'test'\"")
            owner = output.split("\n")[1]
            assert owner == "test", f"Expected database owner to be 'test', got '{owner}'"

            # check if restore works if the database does not exist
            machine.succeed("runuser -u postgres -- dropdb test")
            machine.succeed("${nodes.machine.clan.core.state.test.postRestoreCommand}")
            machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -d test -c '\dt' >&2")
          '';
      };
    };
}
