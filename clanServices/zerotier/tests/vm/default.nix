{
  name = "zerotier";

  clan = {
    directory = ./.;
    test.useContainers = false;
    inventory = {

      machines.jon = { };
      machines.sara = { };
      machines.bam = { };

      instances = {
        autologin = {
          module.name = "importer";
          roles.default.tags.all = { };
          roles.default.extraModules = [
            {
              services.getty.autologinUser = "root";
            }
          ];
        };

        "zerotier" = {
          module.name = "zerotier";
          module.input = "self";

          roles.peer.tags.all = { };
          roles.controller.machines.bam = { };
          roles.moon.machines = { };
        };
      };
    };
  };

  testScript = ''
    start_all()

    # Wait for bam's zerotierone service to start
    bam.wait_for_unit("zerotierone.service")

    # Check controller.json permissions and contents
    print("=== controller.json permissions ===")
    print(bam.succeed("ls -la /var/lib/zerotier-one/controller.json"))

    print("=== controller.json contents ===")
    print(bam.succeed("cat /var/lib/zerotier-one/controller.json"))

    # Show zerotierone service logs
    print("=== zerotierone.service logs ===")
    print(bam.succeed("journalctl -u zerotierone.service -n 100"))
  '';
}
