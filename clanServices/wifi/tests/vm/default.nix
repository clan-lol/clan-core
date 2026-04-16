{
  name = "wifi";

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

        wg-test-open = {
          module.name = "@clan/wifi";
          module.input = "self";

          roles.default.machines = {
            test.settings.networks.open.keyMgmt = "none";
          };
        };
      };
    };
  };

  testScript = ''
    start_all()
    test.wait_for_unit("NetworkManager.service")
    psk = test.succeed("cat /run/NetworkManager/system-connections/one.nmconnection")
    assert "mock-prompt-value-password" in psk, f"Expected mock password in connection file:\n{psk}"

    # key-mgmt=none: no password entry in secrets file, no wifi-security section in connection file
    secrets = test.succeed("cat /run/secrets/NetworkManager/wifi-secrets")
    assert "pw_open=" not in secrets, f"Expected no pw_open= in secrets file:\n{secrets}"
    open_conn = test.succeed("cat /run/NetworkManager/system-connections/open.nmconnection")
    assert "wifi-security" not in open_conn, f"Expected no wifi-security section in open connection file:\n{open_conn}"
  '';
}
