{
  name = "matrix-synapse";

  clan = {
    directory = ./.;
    inventory = {

      machines.machine = { };

      instances = {
        matrix-synaps = {
          module.name = "@clan/matrix-synapse";
          module.input = "self";
          roles.default.machines."machine".settings = {
            acmeEmail = "admins@clan.lol";
            server_tld = "clan.test";
            app_domain = "matrix.clan.test";
            users.admin.admin = true;
            users.someuser = { };
          };
        };
      };
    };
  };

  nodes.machine =
    { lib, pkgs, ... }:
    {

      environment.systemPackages = with pkgs; [
        curl
        netcat
      ];

      services.nginx.virtualHosts."matrix.clan.test" = {
        enableACME = lib.mkForce false;
        forceSSL = lib.mkForce false;
      };

    };

  testScript = ''

    start_all()
    machine.wait_for_unit("matrix-synapse")
    machine.succeed("nc -z -v ::1 8008")
    machine.wait_until_succeeds("curl -Ssf -L http://localhost/_matrix/static/ -H 'Host: matrix.clan.test'")

    machine.systemctl("restart matrix-synapse >&2") # check if user creation is idempotent
    machine.execute("journalctl -u matrix-synapse --no-pager >&2")
    machine.wait_for_unit("matrix-synapse")
    machine.succeed("nc -z -v ::1 8008")
    machine.succeed("curl -Ssf -L http://localhost/_matrix/static/ -H 'Host: matrix.clan.test'")

  '';
}
