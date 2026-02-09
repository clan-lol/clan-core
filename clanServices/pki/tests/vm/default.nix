{
  name = "pki";

  clan = {
    directory = ./.;

    # SSL does not work in containers
    test.useContainers = false;

    modules.test-webservice-nginx = ./test-webservice-nginx.nix;
    modules.test-webservice-caddy = ./test-webservice-caddy.nix;

    inventory = {
      meta.domain = "test";

      machines.nginx = { };
      machines.caddy = { };
      machines.client = { };

      instances = {
        pki = {
          module.name = "@clan/pki";
          module.input = "self";
          roles.default.machines.nginx = { };
          roles.default.machines.caddy = { };
          roles.default.machines.client = { };
        };

        webservice-nginx = {
          module.name = "test-webservice-nginx";
          module.input = "self";
          roles.default.machines.nginx = { };
        };

        webservice-caddy = {
          module.name = "test-webservice-caddy";
          module.input = "self";
          roles.default.machines.caddy = { };
        };
      };
    };
  };

  nodes =
    let
      hostConfig = ''
        192.168.1.3 website.nginx.test
        192.168.1.1 website.caddy.test
      '';
    in
    {
      nginx.networking.extraHosts = hostConfig;
      caddy.networking.extraHosts = hostConfig;
      client.networking.extraHosts = hostConfig;
    };

  testScript = ''
    start_all()

    nginx.wait_for_unit("nginx.service")
    caddy.wait_for_unit("caddy.service")

    # curl will fail if the certificate is not trusted
    client.wait_until_succeeds("curl -v https://website.nginx.test")
    client.wait_until_succeeds("curl -v https://website.caddy.test")
  '';
}
