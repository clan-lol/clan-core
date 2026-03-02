{
  name = "dm-dns";

  clan = {
    directory = ./.;

    modules.test-endpoint = ./test-endpoint.nix;

    inventory = {
      meta.domain = "test";

      machines.server = { };
      machines.client = { };

      instances = {
        dm-dns = {
          module.name = "@clan/dm-dns";
          module.input = "self";
          roles.default.machines.server = { };
          roles.default.machines.client = { };
          roles.default.extraModules = [
            (
              { pkgs, lib, ... }:
              {
                environment.systemPackages = [ pkgs.dnsutils ];

                services.data-mesher.settings = {
                  log_level = lib.mkForce "debug";
                  # reduce this interval to speed up the test
                  cluster.push_pull_interval = lib.mkForce "5s";
                };
              }
            )
          ];

          roles.push.machines.server = { };
          roles.push.extraModules = [
            (
              { lib, ... }:
              {
                # Deploy the signing key so the test can use it to push zone files
                clan.core.vars.generators.dm-dns-signing-key.files."signing.key".deploy = lib.mkForce true;
              }
            )
          ];
        };

        test-endpoint = {
          module.name = "test-endpoint";
          module.input = "self";
          roles.default.machines.server = { };
        };

        data-mesher = {
          module.name = "data-mesher";
          roles.default.machines.server = { };
          roles.default.machines.client = { };
          roles.bootstrap.machines = {
            client = { };
            server = { };
          };
        };
      };
    };
  };

  nodes = {
    server.networking.hosts."10.0.0.1" = [ "server.test" ];
    client.networking.hosts."10.0.0.1" = [ "server.test" ];
  };

  testScript =
    { nodes, ... }:
    let
      inherit (nodes.server.clan.core.vars) generators;

      networkID = generators.data-mesher-network.files."network.pub".path;
      signingKeyPath = generators.dm-dns-signing-key.files."signing.key".path;
      zoneConfPath = generators.dm-dns.files."zone.conf".path;
    in
    ''
      start_all()

      # Wait for services to start
      server.wait_for_unit("unbound.service")
      client.wait_for_unit("unbound.service")
      server.wait_for_unit("data-mesher.service")

      # Verify A record from networking.hosts resolves via unbound
      server.wait_until_succeeds("dig +short @127.0.0.1 -p 5353 server.test A | grep 10.0.0.1")

      # Sign and push the zone file to data-mesher
      server.succeed("data-mesher file update --network-id ${networkID} ${zoneConfPath} --url http://localhost:7331 --key ${signingKeyPath} --name dns/cnames")

      # The path watcher (unbound-reload-zones.path) should trigger an unbound reload.
      # Wait until the CNAME record resolves.
      server.wait_until_succeeds("dig +short @127.0.0.1 -p 5353 myapp.test CNAME | grep server.test", timeout=30)
    '';
}
