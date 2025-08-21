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
          '';
      };
    };
}
