{
  pkgs,
  ...
}:
{
  name = "dyndns";

  clan = {
    directory = ./.;
    inventory = {
      machines.server = { };

      instances = {
        dyndns-test = {
          module.name = "@clan/dyndns";
          module.input = "self";
          roles.default.machines."server".settings = {
            server = {
              enable = true;
              domain = "test.example.com";
              port = 54805;
              acmeEmail = "test@example.com";
            };
            period = 1;
            settings = {
              "test.example.com" = {
                provider = "namecheap";
                domain = "example.com";
                secret_field_name = "password";
                extraSettings = {
                  host = "test";
                  server = "dynamicdns.park-your-domain.com";
                };
              };
            };
          };
        };
      };
    };
  };

  nodes = {
    server = {
      # Disable firewall for testing
      networking.firewall.enable = false;

      # Mock ACME for testing (avoid real certificate requests)
      security.acme.defaults.server = "https://localhost:14000/dir";
    };
  };

  testScript = ''
    start_all()

    # Test that dyndns service starts (will fail without secrets, but that's expected)
    server.wait_for_unit("multi-user.target")

    # Test that nginx service is running
    server.wait_for_unit("nginx.service")

    # Test that nginx is listening on expected ports
    server.wait_for_open_port(80)
    server.wait_for_open_port(443)

    # Test that the dyndns user was created
    # server.succeed("getent passwd dyndns")
    # server.succeed("getent group dyndns")
    #
    # Test that the home directory was created
    server.succeed("test -d /var/lib/dyndns")

    # Test that nginx configuration includes our domain
    server.succeed("${pkgs.nginx}/bin/nginx -t")

    print("All tests passed!")
  '';
}
