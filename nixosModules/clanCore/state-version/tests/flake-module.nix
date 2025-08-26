{ ... }:
{
  perSystem =
    { ... }:
    {
      clan.nixosTests.state-version = {

        name = "service-state-version";

        clan = {
          directory = ./.;
          machines.server = {
            clan.core.settings.state-version.enable = true;
          };
        };

        # This is not an actual vm test, this is a workaround to
        # generate the needed vars for the eval test.
        testScript = "";
      };
    };
}
