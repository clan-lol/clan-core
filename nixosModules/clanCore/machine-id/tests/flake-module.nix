{
  perSystem.clan.nixosTests.machine-id = {

    name = "service-machine-id";

    clan = {
      directory = ./.;
      machines.server = {
        clan.core.settings.machine-id.enable = true;
      };
    };

    # This is not an actual vm test, this is a workaround to
    # generate the needed vars for the eval test.
    testScript = "";
  };
}
