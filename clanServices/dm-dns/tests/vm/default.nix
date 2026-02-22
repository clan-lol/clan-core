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
              { pkgs, ... }:
              {
                environment.systemPackages = [ pkgs.dnsutils ];
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
      signingKeyPath =
        nodes.server.config.clan.core.vars.generators.dm-dns-signing-key.files."signing.key".path;
      zoneConfPath = nodes.server.config.clan.core.vars.generators.dm-dns.files."zone.conf".path;
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
      server.succeed("data-mesher file update ${zoneConfPath} --url http://localhost:7331 --key ${signingKeyPath} --name dns/cnames")

      # The path watcher (unbound-reload-zones.path) should trigger an unbound reload.
      # Wait until the CNAME record resolves.
      server.wait_until_succeeds("dig +short @127.0.0.1 -p 5353 myapp.test CNAME | grep server.test", timeout=30)
    '';
}
