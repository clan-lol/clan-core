{
  pkgs,
  ...
}:
{
  name = "ncps";

  clan = {
    directory = ./.;
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
      services.harmonia = {
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
      # Check harmonia is running
      clare.succeed("systemctl status harmonia")

      # Check that ncps is listening on its default port
      alice.wait_until_succeeds("curl bob:8502/nix-cache-info", 10)
      # Check that harmonia is accessible from bob
      bob.wait_until_succeeds("curl clare:5000/nix-cache-info", 10)

      build_log = clare.succeed("""${trivialBuild}""")
      # Ensure Clare is really building the derivation
      assert "building" in build_log

      build_log = alice.succeed("""${trivialBuild}""")
      # Ensure Alice is **not** building the derivation: substitution works
      assert "building" not in build_log
    '';
}
