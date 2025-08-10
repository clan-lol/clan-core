{ ... }:
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

                  clan.core.postgresql.enable = true;
                  clan.core.postgresql.users.test = { };
                  clan.core.postgresql.databases.test.create.options.OWNER = "test";
                  clan.core.settings.directory = ./.;

                }
              ];
            };
          };
        };

        # TODO: Broken. Use instead of importer after fixing.
        # nodes.machine = { };

        testScript = ''
          start_all()
          machine.wait_for_unit("postgresql")

          # Create a test table
          machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -c 'CREATE TABLE test (id serial PRIMARY KEY);' test")
          machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -d test -c 'INSERT INTO test DEFAULT VALUES;'")
          machine.succeed("runuser -u postgres -- /run/current-system/sw/bin/psql -d test -c 'SELECT * FROM test;'")
        '';
      };
    };
}
