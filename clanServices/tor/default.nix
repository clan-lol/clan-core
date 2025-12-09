{
  lib,
  clanLib,
  config,
  directory,
  ...
}:
{
  _class = "clan.service";
  manifest.name = "clan-core/tor";
  manifest.description = "Part of the clan networking abstraction to define how to reach machines through the Tor network, if used has the lowest priority";
  manifest.categories = [
    "System"
    "Network"
  ];
  manifest.readme = builtins.readFile ./README.md;

  exports = lib.mapAttrs' (instanceName: _: {
    name = clanLib.buildScopeKey {
      inherit instanceName;
      serviceName = config.manifest.name;
    };
    value = {
      networking.priority = 10;
    };
  }) config.instances;

  roles.client = {
    description = ''
      Enables a continuosly running Tor proxy on the machine, allowing access to other machines via the Tor network.
      If not enabled, a Tor proxy will be started automatically when required.
    '';
    perInstance =
      {
        ...
      }:
      {
        nixosModule =
          {
            ...
          }:
          {
            config = {
              services.tor = {
                enable = true;
                torsocks.enable = true;
                client.enable = true;
              };
            };
          };
      };
  };

  roles.server = {
    description = "Sets up a Tor onion service for the machine, thus making it reachable over Tor.";
    interface =
      { lib, ... }:
      {
        options = {

          portMapping = lib.mkOption {
            type = lib.types.listOf lib.types.raw;
            default = [
              {
                port = 22;
                target.port = 22;
              }
            ];
            description = ''
              List of port mappings for the Tor onion service.
              Each mapping defines which ports are exposed through Tor and where they should forward to.
              Default exposes SSH (port 22) for remote access.
            '';
          };

          secretHostname = lib.mkOption {
            type = lib.types.bool;
            default = true;
            description = ''
              Whether to keep the onion service hostname secret.

              When enabled (default), the hostname is stored securely as a
              secret var and not exposed in your configuration.

              If you expose SSH, it is recommended to keep this set to true in
              public configurainos as anyone with knowledge of the hostname
              could try brut-forcing attacks against it.
            '';
          };
        };
      };
    perInstance =
      {
        instanceName,
        mkExports,
        machine,
        settings,
        ...
      }:
      {
        exports = mkExports {
          peer.hosts = [
            {
              var = {
                machine = machine.name;
                generator = "tor_${instanceName}";
                file = "hostname";
                flake = directory;
              };
            }
          ];
        };
        nixosModule =
          {
            pkgs,
            config,
            ...
          }:
          {
            config = {
              services.tor = {
                enable = true;
                relay.onionServices."clan_${instanceName}" = {
                  version = 3;
                  map = settings.portMapping;
                  secretKey = config.clan.core.vars.generators."tor_${instanceName}".files.hs_ed25519_secret_key.path;
                };
              };
              clan.core.vars.generators."tor_${instanceName}" = {
                files.hs_ed25519_secret_key = { };
                files.hostname.secret = settings.secretHostname;
                runtimeInputs = with pkgs; [
                  coreutils
                  tor
                ];
                script = ''
                  mkdir -p data
                  echo -e "DataDirectory ./data\nSocksPort 0\nHiddenServiceDir ./hs\nHiddenServicePort 80 127.0.0.1:80" > torrc
                  timeout 2 tor -f torrc || :
                  mv hs/hs_ed25519_secret_key $out/hs_ed25519_secret_key
                  mv hs/hostname $out/hostname
                '';
              };
            };
          };
      };
  };
}
