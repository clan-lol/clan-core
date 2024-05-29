(import ../lib/container-test.nix) (
  { pkgs, ... }:
  {
    name = "matrix-synapse";

    nodes.machine =
      { self, lib, ... }:
      {
        imports = [
          self.clanModules.matrix-synapse
          self.nixosModules.clanCore
          {
            clanCore.machineName = "machine";
            clanCore.clanDir = ./.;
            clan.matrix-synapse = {
              domain = "clan.test";
            };
          }
          {
            # secret override
            clanCore.facts.services.matrix-synapse.secret.synapse-registration_shared_secret.path = "${./synapse-registration_shared_secret}";
            services.nginx.virtualHosts."matrix.clan.test" = {
              enableACME = lib.mkForce false;
              forceSSL = lib.mkForce false;
            };
          }
        ];
      };
    testScript = ''
      start_all()
      machine.wait_for_unit("matrix-synapse")
      machine.succeed("${pkgs.netcat}/bin/nc -z -v ::1 8008")
      machine.succeed("${pkgs.curl}/bin/curl -Ssf -L http://localhost/_matrix/static/ -H 'Host: matrix.clan.test'")
    '';
  }
)
