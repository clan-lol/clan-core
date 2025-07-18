{
  name = "service-wifi";

  clan = {
    directory = ./.;
    test.useContainers = false;
    inventory = {

      machines.test = { };
      machines.second = { };

      instances = {
        wg-test-all = {
          module.name = "@clan/wifi";
          module.input = "self";
          roles.default.tags.all = { };
          roles.default.settings.networks.all = { };
        };

        wg-test-one = {
          module.name = "@clan/wifi";
          module.input = "self";

          roles.default.machines = {
            test.settings.networks.one = { };
          };
        };
      };
    };
  };

  testScript = ''
    start_all()
    test.wait_for_unit("NetworkManager.service")
    psk = test.succeed("cat /run/NetworkManager/system-connections/one.nmconnection")
    assert "password-eins" in psk, "Password is incorrect"
  '';
}
