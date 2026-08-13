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

  # Defined under `containers` (not `nodes`) because the clan test framework
  # routes inventory machines to `containers.<name>` when useContainers=true
  # (the default). Definitions on `nodes.<name>` would not merge with the
  # clan-derived machine module and would fail evaluation of `clan.*` options.
  containers.machine =
    { lib, pkgs, ... }:
    {

      environment.systemPackages = with pkgs; [
        curl
        netcat
      ];

      # ACME cannot reach Let's Encrypt from inside the build sandbox, so the
      # acme-*.service units never finish and nginx (which Wants= them) never
      # reaches active state -- the container then fails to hit default.target
      # within the test driver's ready-state timeout.
      # The matrix-synapse service registers two vhosts (server_tld and
      # app_domain); both must opt out for nginx to start cleanly.
      services.nginx.virtualHosts."clan.test" = {
        enableACME = lib.mkForce false;
        forceSSL = lib.mkForce false;
      };
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

    # Restarting re-runs the ExecStartPost user-registration script, which calls
    # register_new_matrix_user with --exists-ok. If registration were not
    # idempotent the start job would report failure; a clean restart plus a
    # working endpoint afterwards proves the users are re-registered without
    # error. This completes in ~15s once nginx no longer stalls boot on ACME
    # (see the enableACME/forceSSL overrides above): the >15min "hang" that
    # previously forced this check to be dropped was the container never
    # reaching default.target under the nspawn driver's readiness wait, not the
    # restart itself.
    machine.systemctl("restart matrix-synapse >&2") # check if user creation is idempotent
    machine.wait_for_unit("matrix-synapse")
    machine.succeed("nc -z -v ::1 8008")
    machine.succeed("curl -Ssf -L http://localhost/_matrix/static/ -H 'Host: matrix.clan.test'")

  '';
}
