{
  pkgs,
  ...
}:
{
  name = "ncps";

  clan = {
    directory = ./.;
    # This test needs real nix stores with a nix database: bob's ncps and
    # clare's harmonia both serve store paths, and alice substitutes from
    # them. nspawn containers get a read-only host store without a database,
    # so this test runs as QEMU VMs.
    test.useContainers = false;
    inventory = {
      # alice is the client, bob the ncps proxy cache and clare an upstream cache
      machines.alice = { };
      machines.bob = { };
      machines.clare = { };

      instances = {
        ncps-test = {
          module.name = "ncps";
          roles.server.machines."bob".settings = {
            caches = [ "http://clare.clan:5000" ];
            publicKeys = [ (builtins.readFile ./auxiliary-harmonia-secrets/pub-key) ];
            port = 8502;
          };
          roles.client.machines."alice" = { };
        };
      };
    };
  };

  nodes = {
    alice = {
      environment.systemPackages = [ pkgs.curl ];
      networking.extraHosts = ''
        192.168.1.2 bob.clan
      '';

    };

    bob = {

      networking.extraHosts = ''
        192.168.1.3 clare.clan
      '';
    };
    clare = {
      networking.firewall.allowedTCPPorts = [ 5000 ];
      services.harmonia.cache = {
        enable = true;
        signKeyPaths = [ ./auxiliary-harmonia-secrets/sign-key ];
      };
    };
  };

  testScript =
    let
      trivialBuild = ''
        nix-build --expr '
          builtins.derivation {
            name = "hi";
            builder = "/bin/sh";
            args = [ "-c" "echo hi > $out" ];
            system = "${pkgs.stdenv.hostPlatform.system}";
          }
        ' 2>&1
      '';
    in
    ''
      start_all()

      # Check that ncps service is running
      bob.wait_for_unit("ncps")
      bob.succeed("systemctl status ncps")
      # harmonia is socket-activated: the service only starts on the first
      # connection, so wait for the socket unit instead of the service
      clare.wait_for_unit("harmonia.socket")

      # Check that ncps is listening on its default port
      alice.wait_until_succeeds("curl bob:8502/nix-cache-info")
      # Check that harmonia is accessible from bob; this first request also
      # triggers the socket activation of the harmonia service
      bob.wait_until_succeeds("curl clare:5000/nix-cache-info")
      clare.wait_for_unit("harmonia")
      clare.succeed("systemctl status harmonia")

      build_log = clare.succeed("""${trivialBuild}""")
      # Ensure Clare is really building the derivation
      assert "building" in build_log

      build_log = alice.succeed("""${trivialBuild}""")
      # Ensure Alice is **not** building the derivation: substitution works
      assert "building" not in build_log
    '';
}
