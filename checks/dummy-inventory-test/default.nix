(import ../lib/test-inventory.nix) (
  { ... }:
  {
    # This tests the compatibility of the inventory
    # With the test framework
    # - legacy-modules
    # - clan.service modules
    name = "dummy-inventory-test";

    clanSettings = {
      self = ./.;
    };
    clan = {
      inventory = {
        machines.peer1 = { };
        machines.admin1 = { };
        services = {
          legacy-module.default = {
            roles.peer.machines = [ "peer1" ];
            roles.admin.machines = [ "admin1" ];
          };
        };
        instances."test" = {
          module.name = "new-service";
          roles.peer.machines.peer1 = { };
        };

        modules = {
          legacy-module = ./legacy-module;
          new-service = {
            _class = "clan.service";
            manifest.name = "new-service";
            roles.peer = { };
            perMachine = {
              nixosModule = {
                # This should be generated by:
                # ./pkgs/scripts/update-vars.py inventory-test-framework-compatibility-test
                clan.core.vars.generators.new-service = {
                  files.hello = {
                    secret = false;
                    deploy = true;
                  };
                  script = ''
                    # This is a dummy script that does nothing
                    echo "This is a dummy script" > $out/hello
                  '';
                };
              };
            };
          };
        };
      };
    };

    testScript =
      { nodes, ... }:
      ''
        start_all()
        admin1.wait_for_unit("multi-user.target")
        peer1.wait_for_unit("multi-user.target")
        # Provided by the legacy module
        print(admin1.succeed("systemctl status dummy-service"))
        print(peer1.succeed("systemctl status dummy-service"))

        # peer1 should have the 'hello' file
        peer1.succeed("cat ${nodes.peer1.clan.core.vars.generators.new-service.files.hello.path}")
      '';
  }
)
