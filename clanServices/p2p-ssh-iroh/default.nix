{
  lib,
  clanLib,
  config,
  ...
}:
{
  _class = "clan.service";
  manifest.name = "clan-core/p2p-ssh-iroh";
  manifest.description = "SSH over dumbpipe (iroh) — NAT-traversing SSH access via encrypted QUIC streams";
  manifest.categories = [
    "System"
    "Network"
  ];
  manifest.readme = builtins.readFile ./README.md;
  manifest.exports.out = [
    "networking"
    "peer"
  ];

  exports = lib.mapAttrs' (instanceName: _: {
    name = clanLib.buildScopeKey {
      inherit instanceName;
      serviceName = config.manifest.name;
    };
    value = {
      networking.priority = 3000;
      networking.module = "clan_lib.network.p2p_ssh_iroh";
    };
  }) config.instances;

  roles.server = {
    description = "Exposes sshd via dumbpipe over iroh, enabling NAT-traversing SSH access.";

    perInstance =
      {
        instanceName,
        mkExports,
        ...
      }:
      {
        # Export peer with empty hosts — the p2p-ssh-iroh Python module reads
        # the dumbpipe ticket directly from vars (not from peer.hosts), since
        # tickets are not routable addresses and must not be consumed by other
        # services (e.g. yggdrasil peering).
        exports = mkExports {
          peer.hosts = [ ];
        };

        nixosModule =
          { config, pkgs, ... }:
          let
            generatorName = "p2p-ssh-iroh-${instanceName}";
            secretPath = config.clan.core.vars.generators.${generatorName}.files.iroh-secret.path;
          in
          {
            clan.core.vars.generators.${generatorName} = {
              files.iroh-secret.secret = true;
              files.ticket.secret = false;
              runtimeInputs = [
                pkgs.openssl
                pkgs.dumbpipe
              ];
              script = ''
                openssl rand -hex 32 > "$out/iroh-secret"
                IROH_SECRET="$(cat "$out/iroh-secret")" dumbpipe generate-ticket | tr -d '\n' > "$out/ticket"
              '';
            };

            services.openssh.enable = true;

            systemd.services."p2p-ssh-iroh-${instanceName}" = {
              description = "Expose sshd via dumbpipe (iroh) [${instanceName}]";
              after = [
                "network-online.target"
                "sshd.service"
              ];
              wants = [ "network-online.target" ];
              wantedBy = [ "multi-user.target" ];

              serviceConfig = {
                LoadCredential = "iroh-secret:${secretPath}";
                ExecStart =
                  let
                    wrapper = pkgs.writeShellScript "p2p-ssh-iroh-${instanceName}" ''
                      export IROH_SECRET
                      IROH_SECRET="$(cat "$CREDENTIALS_DIRECTORY/iroh-secret")"
                      exec ${pkgs.dumbpipe}/bin/dumbpipe listen-tcp --host 127.0.0.1:22
                    '';
                  in
                  "${wrapper}";
                Restart = "always";
                RestartSec = 5;
                DynamicUser = true;

                ProtectSystem = "strict";
                ProtectHome = true;
                PrivateTmp = true;
                NoNewPrivileges = true;
              };
            };
          };
      };
  };
}
