{ ... }:
{
  perSystem =
    { ... }:
    {
      clan.nixosTests.machine-id = {

        name = "machine-id";

        clan = {
          directory = ./.;

          # Workaround until we can use nodes.server = { };
          modules."@clan/importer" = ../../../../clanServices/importer;

          inventory = {
            machines.server = { };
            instances.importer = {
              module.name = "@clan/importer";
              roles.default.tags.all = { };
              roles.default.extraModules = [
                {
                  # Test machine ID generation
                  clan.core.settings.machine-id.enable = true;
                }
              ];
            };
          };
        };

        # TODO: Broken. Use instead of importer after fixing.
        # nodes.server = { };

        # This is not an actual vm test, this is a workaround to
        # generate the needed vars for the eval test.
        testScript = "";
      };
    };
}
