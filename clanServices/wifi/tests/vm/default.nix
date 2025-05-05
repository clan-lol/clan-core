{
  pkgs,
  self,
  clanLib,
  module,
  ...
}:
clanLib.test.makeTestClan {
  inherit pkgs self;
  useContainers = false;
  nixosTest = (
    { ... }:
    {
      name = "wifi";

      clan = {
        directory = ./.;
        inventory = {
          modules."@clan/wifi" = module;

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
        test.wait_for_unit("iwd.service")
        psk = test.succeed("cat /var/lib/iwd/ssid-one.psk")
        assert "password-eins" in psk, "Password is incorrect"
      '';
    }
  );
}
