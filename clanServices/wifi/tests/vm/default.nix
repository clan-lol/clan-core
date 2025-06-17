{
  name = "wifi";

  clan = {
    directory = ./.;
    test.useContainers = false;
    inventory = {

      machines.test = { };

      instances = {
        wg-test-one = {
          module.name = "@clan/wifi";

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
