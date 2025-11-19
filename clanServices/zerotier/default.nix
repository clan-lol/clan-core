{
  clanLib,
  config,
  lib,
  directory,
  ...
}:
{
  _class = "clan.service";
  manifest.name = "clan-core/zerotier";
  manifest.description = "Zerotier Mesh VPN Service for secure P2P networking between machines";
  manifest.categories = [ "Utility" ];
  manifest.readme = builtins.readFile ./README.md;


          # networking.priority = lib.mkDefault 900;

  exports = lib.mapAttrs' (instanceName: _: {
    name = clanLib.exports.buildScopeKey {
      inherit instanceName;
      serviceName = config.manifest.name;
    };
    value = {
      networking.priority = 900;
    };
  }) config.instances;

  roles.peer = {
    description = "A peer that connects to your private Zerotier network.";
    perInstance =
      {
        instanceName,
        roles,
        mkExports,
        machine,
        ...
      }:
      {
        exports = mkExports {
          peer.host.plain = clanLib.vars.getPublicValue {
            machine = machine.name;
            generator = "zerotier";
            file = "zerotier-ip";
            flake = directory;
          };
        };
        nixosModule =
          {
            config,
            lib,
            pkgs,
            ...
          }:
          {
            imports = [
              (import ./shared.nix {
                inherit
                  clanLib
                  instanceName
                  roles
                  config
                  lib
                  pkgs
                  ;
              })
            ];
          };
      };
  };

  roles.moon = {
    description = "A moon acts as a relay node to connect other nodes in the zerotier network that are not publicly reachable. Each moon must be publicly reachable.";
    interface =
      { lib, ... }:
      {
        options.stableEndpoints = lib.mkOption {
          type = lib.types.listOf lib.types.str;
          description = ''
            Make this machine a moon.
            Other machines can join this moon by adding this moon in their config.
            It will be reachable under the given stable endpoints.
          '';
          example = ''
            [ "1.2.3.4" "10.0.0.3/9993" "2001:abcd:abcd::3/9993" ]
          '';
        };

      };
    perInstance =
      {
        instanceName,
        settings,
        roles,
        ...
      }:
      {
        nixosModule =
          {
            config,
            lib,
            pkgs,
            ...
          }:
          {
            config.clan.core.networking.zerotier.moon.stableEndpoints = settings.stableEndpoints;

            imports = [
              (import ./shared.nix {
                inherit
                  clanLib
                  instanceName
                  roles
                  config
                  lib
                  pkgs
                  ;
              })
            ];
          };
      };
  };

  roles.controller = {
    description = "Manages network membership and is responsible for admitting new peers to your Zerotier network.";
    interface =
      { lib, ... }:
      {
        options.allowedIps = lib.mkOption {
          type = lib.types.listOf lib.types.str;
          default = [ ];
          description = ''
            Extra machines by their zerotier ip that the zerotier controller
            should accept. These could be external machines.
          '';
          example = ''
            [ "fd5d:bbe3:cbc5:fe6b:f699:935d:bbe3:cbc5" ]
          '';
        };
      };

    perInstance =
      {
        instanceName,
        roles,
        settings,
        ...
      }:
      {
        nixosModule =
          {
            config,
            lib,
            pkgs,
            ...
          }:
          let
            uniqueStrings = list: builtins.attrNames (builtins.groupBy lib.id list);
          in
          {
            imports = [
              (import ./shared.nix {
                inherit
                  clanLib
                  instanceName
                  roles
                  config
                  lib
                  pkgs
                  ;
              })
            ];
            config = {
              systemd.services.zerotier-inventory-autoaccept =
                let
                  machines = uniqueStrings (
                    (lib.optionals (roles ? moon) (lib.attrNames roles.moon.machines))
                    ++ (lib.optionals (roles ? controller) (lib.attrNames roles.controller.machines))
                    ++ (lib.optionals (roles ? peer) (lib.attrNames roles.peer.machines))
                  );
                  networkIps = builtins.foldl' (
                    ips: name:
                    let
                      ztIp = clanLib.vars.getPublicValue {
                        flake = config.clan.core.settings.directory;
                        machine = name;
                        generator = "zerotier";
                        file = "zerotier-ip";
                        default = null;
                      };
                    in
                    if ztIp != null then ips ++ [ ztIp ] else ips
                  ) [ ] machines;
                  allHostIPs = settings.allowedIps ++ networkIps;
                in
                {
                  wantedBy = [ "multi-user.target" ];
                  after = [ "zerotierone.service" ];
                  path = [ config.clan.core.clanPkgs.zerotierone ];
                  serviceConfig.ExecStart = pkgs.writeShellScript "zerotier-inventory-autoaccept" ''
                    ${lib.concatMapStringsSep "\n" (host: ''
                      ${config.clan.core.clanPkgs.zerotier-members}/bin/zerotier-members allow --member-ip ${host}
                    '') allHostIPs}
                  '';
                };

              clan.core.networking.zerotier.controller.enable = lib.mkDefault true;
            };

          };
      };
  };
}
