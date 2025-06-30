{ ... }:
{
  perSystem =
    { ... }:
    {
      clan.nixosTests.state-version = {

        name = "service-state-version";

        clan = {
          directory = ./.;

          # Workaround until we can use nodes.server = { };
          modules."@clan/importer" = ../../../../clanServices/importer;

          inventory = {
            machines.server = { };
            instances.importer = {
              module.name = "@clan/importer";
              module.input = "self";
              roles.default.tags.all = { };
              roles.default.extraModules = [
                {
                  clan.core.settings.state-version.enable = true;
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
