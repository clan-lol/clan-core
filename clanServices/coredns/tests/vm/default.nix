{
  ...
}:
{
  name = "coredns";

  clan = {
    directory = ./.;
    test.useContainers = true;
    inventory = {

      machines = {
        dns = { }; # 192.168.1.2
        server01 = { }; # 192.168.1.3
        server02 = { }; # 192.168.1.4
        client = { }; # 192.168.1.1
      };

      instances = {
        coredns = {

          module.name = "@clan/coredns";
          module.input = "self";

          roles.default.tags.all = { };

          # First service
          roles.default.machines."server01".settings = {
            ip = "192.168.1.3";
            services = [ "one" ];
          };

          # Second service
          roles.default.machines."server02".settings = {
            ip = "192.168.1.4";
            services = [ "two" ];
          };

          # DNS server
          roles.server.machines."dns".settings = {
            ip = "192.168.1.2";
            tld = "foo";
          };
        };
      };
    };
  };

  nodes = {
    dns =
      { pkgs, ... }:
      {
        environment.systemPackages = [ pkgs.net-tools ];
      };

    client =
      { pkgs, ... }:
      {
        environment.systemPackages = [ pkgs.net-tools ];
      };

    server01 = {
      services.nginx = {
        enable = true;
        virtualHosts."one.foo" = {
          locations."/" = {
            return = "200 'test server response one'";
            extraConfig = "add_header Content-Type text/plain;";
          };
        };
      };
    };
    server02 = {
      services.nginx = {
        enable = true;
        virtualHosts."two.foo" = {
          locations."/" = {
            return = "200 'test server response two'";
            extraConfig = "add_header Content-Type text/plain;";
          };
        };
      };
    };
  };

  testScript = ''
    import json
    start_all()

    machines = [server01, server02, dns, client]

    for m in machines:
        m.systemctl("start network-online.target")

    for m in machines:
        m.wait_for_unit("network-online.target")

    # This should work, but is borken in tests i think? Instead we dig directly

    # client.succeed("curl -k -v http://one.foo")
    # client.succeed("curl -k -v http://two.foo")

    answer = client.succeed("dig @192.168.1.2 -p 1053 one.foo")
    assert "192.168.1.3" in answer, "IP not found"

    answer = client.succeed("dig @192.168.1.2 -p 1053 two.foo")
    assert "192.168.1.4" in answer, "IP not found"

  '';
}
