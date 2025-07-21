{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/zerotier";
  manifest.description = "Configuration of the secure and efficient Zerotier VPN";
  manifest.categories = [ "Utility" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.peer = {
    perInstance =
      { instanceName, roles, ... }:
      {
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
            [ 1.2.3.4" "10.0.0.3/9993" "2001:abcd:abcd::3/9993" ]
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
                    if
                      builtins.pathExists "${config.clan.core.settings.directory}/vars/per-machine/${name}/zerotier/zerotier-ip/value"
                    then
                      ips
                      ++ [
                        (builtins.readFile "${config.clan.core.settings.directory}/vars/per-machine/${name}/zerotier/zerotier-ip/value")
                      ]
                    else
                      ips
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
