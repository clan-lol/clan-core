{
  pkgs,
  ...
}:
{
  name = "garage";

  clan = {
    directory = ./.;
    inventory = {
      machines.server = { };

      instances = {
        garage-test = {
          module.name = "@clan/garage";
          module.input = "self";
          roles.default.machines."server".settings = { };
        };
      };
    };
  };

  nodes = {
    server = {
      services.garage = {
        enable = true;
        package = pkgs.garage;
        settings = {

          metadata_dir = "/var/lib/garage/meta";
          data_dir = "/var/lib/garage/data";
          db_engine = "sqlite";

          replication_factor = 1;

          rpc_bind_addr = "127.0.0.1:3901";

          s3_api = {
            api_bind_addr = "127.0.0.1:3900";
            s3_region = "garage";
            root_domain = ".s3.garage";
          };

          s3_web = {
            bind_addr = "127.0.0.1:3902";
            root_domain = ".web.garage";
          };

          admin = {
            api_bind_addr = "127.0.0.1:3903";
          };
        };
      };
    };
  };

  testScript = ''
    start_all()

    server.wait_for_unit("network-online.target")
    server.wait_for_unit("garage")

    # Check that garage is running
    server.succeed("systemctl status garage")

    # Check that the data directories exist
    server.succeed("test -d /var/lib/garage/meta")
    server.succeed("test -d /var/lib/garage/data")

    # Check that the ports are open to confirm that garage is running
    server.wait_until_succeeds("${pkgs.netcat}/bin/nc -z -v 127.0.0.1 3901")
    server.succeed("${pkgs.netcat}/bin/nc -z -v 127.0.0.1 3900")
    server.succeed("${pkgs.netcat}/bin/nc -z -v 127.0.0.1 3902")
    server.succeed("${pkgs.netcat}/bin/nc -z -v 127.0.0.1 3903")
  '';
}
