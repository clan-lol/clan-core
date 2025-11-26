{
  clanLib,
  lib,
  config,
  directory,
  ...
}:
{
  _class = "clan.service";
  manifest.name = "clan-core/mycelium";
  manifest.description = "End-2-end encrypted P2P IPv6 overlay network";
  manifest.categories = [
    "System"
    "Network"
  ];
  manifest.readme = builtins.readFile ./README.md;

  exports = lib.mapAttrs' (instanceName: _: {
    name = clanLib.exports.buildScopeKey {
      inherit instanceName;
      serviceName = config.manifest.name;
    };
    value = {
      networking.priority = 800;
    };
  }) config.instances;

  roles.peer = {
    description = "A peer in the mycelium network";
    interface =
      { lib, ... }:
      {
        options = {
          openFirewall = lib.mkOption {
            type = lib.types.bool;
            default = true;
            description = "Open the firewall for mycelium";
          };

          addHostedPublicNodes = lib.mkOption {
            type = lib.types.bool;
            default = true;
            description = "Add hosted Public nodes";
          };
        };
      };

    perInstance =
      {
        settings,
        mkExports,
        machine,
        ...
      }:
      {

        exports = mkExports {
          peer.hosts = [
            {
              plain = clanLib.vars.getPublicValue {
                machine = machine.name;
                generator = "mycelium";
                file = "ip";
                flake = directory;
              };
            }
          ];
        };

        nixosModule =
          {
            config,
            pkgs,
            lib,
            ...
          }:
          {
            services.mycelium = {
              enable = true;
              addHostedPublicNodes = lib.mkDefault settings.addHostedPublicNodes;
              openFirewall = lib.mkDefault settings.openFirewall;
              keyFile = config.clan.core.vars.generators.mycelium.files.key.path;
            };

            clan.core.vars.generators.mycelium = {
              files.key = { };
              files.ip.secret = false;
              files.pubkey.secret = false;
              runtimeInputs = [
                pkgs.mycelium
                pkgs.coreutils
                pkgs.jq
              ];
              script = ''
                timeout 5 mycelium --key-file "$out"/key || :
                mycelium inspect --key-file "$out"/key --json | jq -r .publicKey > "$out"/pubkey
                mycelium inspect --key-file "$out"/key --json | jq -r .address > "$out"/ip
              '';
            };
          };
      };
  };
}
