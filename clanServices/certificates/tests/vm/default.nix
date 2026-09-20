{
  name = "certificates";

  clan = {
    directory = ./.;
    inventory = {

      machines.ca = { }; # 192.168.1.1
      machines.client = { }; # 192.168.1.2
      machines.server = { }; # 192.168.1.3

      instances."certificates" = {
        module.name = "certificates";
        module.input = "self";

        roles.ca.machines.ca.settings.tlds = [ "foo" ];
        roles.default.machines.client = { };
        roles.default.machines.server = { };
      };
    };
  };

  containers =
    let
      hostConfig = ''
        192.168.1.1 ca.foo
        192.168.1.3 test.foo
      '';
    in
    {

      client.networking.extraHosts = hostConfig;
      ca.networking.extraHosts = hostConfig;

      server = {

        networking.extraHosts = hostConfig;

        # TODO: Could this be set automatically?
        # I would like to get this information from the coredns module, but we
        # cannot model dependencies yet
        security.acme.certs."test.foo".server = "https://ca.foo/acme/acme/directory";

        # Host a simple service on 'server', with SSL provided via our CA. 'client'
        # should be able to curl it via https and accept the certificates
        # presented
        networking.firewall.allowedTCPPorts = [
          80
          443
        ];

        services.nginx = {
          enable = true;
          virtualHosts."test.foo" = {
            enableACME = true;
            forceSSL = true;
            locations."/" = {
              return = "200 'test server response'";
              extraConfig = "add_header Content-Type text/plain;";
            };
          };
        };
      };
    };

  testScript = ''
    # Start CA first and let it issue its own cert
    ca.start()
    ca.wait_for_unit("step-ca.service")
    ca.wait_for_file("/var/lib/acme/ca.foo/fullchain.pem")

    # Restart nginx so it actively serves the newly issued cert
    ca.succeed("systemctl restart nginx.service")

    # Start server and client now that the CA is fully operational
    server.start()
    client.start()

    # Wait for server to obtain its certificate and restart nginx
    server.wait_for_file("/var/lib/acme/test.foo/fullchain.pem")
    server.succeed("systemctl restart nginx.service")

    # It takes a while for the correct certs to appear (before that self-signed
    # are presented by nginx) so we wait for a bit.
    client.wait_until_succeeds("curl -v https://test.foo")

    # Show certificate information for debugging
    client.succeed("openssl s_client -connect test.foo:443 -servername test.foo </dev/null 2>/dev/null | openssl x509 -text -noout 1>&2")
  '';
}
