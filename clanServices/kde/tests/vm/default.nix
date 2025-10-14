{
  name = "kde";

  clan = {
    directory = ./.;
    inventory = {

      machines.client = { };

      instances = {
        kde = {
          module.name = "kde";
          module.input = "self";
          roles.default.machines."client" = { };
        };
      };
    };
  };

  testScript = ''
    start_all()

    client.systemctl("start network-online.target")
    client.wait_for_unit("network-online.target")

    client.wait_for_unit("graphical.target")
    client.wait_for_unit("display-manager.service")
    client.succeed("systemctl status display-manager.service")
  '';
}
