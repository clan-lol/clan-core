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
  manifest.description = "ZeroTier Mesh VPN Service for secure P2P networking between machines";
  manifest.categories = [ "Network" ];
  manifest.readme = builtins.readFile ./README.md;
  manifest.exports.out = [
    "networking"
    "peer"
  ];
  # Require exactly one controller per network
  manifest.constraints.roles.controller.maxMachines = 1;
  manifest.constraints.roles.controller.minMachines = 1;
  # Max 4 roots per moon definition (zerotier-idtool 1.x limit).
  # See https://github.com/zerotier/ZeroTierOne/issues/893
  manifest.constraints.roles.moon.maxMachines = 4;

  exports = lib.mapAttrs' (instanceName: _: {
    name = clanLib.buildScopeKey {
      inherit instanceName;
      serviceName = config.manifest.name;
    };
    value = {
      networking.priority = 900;
      networking.module = "clan_lib.network.zerotier";
    };
  }) config.instances;

  roles.peer = {
    description = "A peer that connects to your private ZeroTier network.";
    interface =
      { lib, ... }:
      {
        options.orbitMoons = lib.mkOption {
          type = lib.types.listOf lib.types.str;
          default = [ ];
          description = ''
            External moon IDs to orbit.
            Use this to join moons that are not declared in the clan inventory.
            Moons declared via the "moon" role are orbited automatically.
          '';
          example = ''
            [ "deadbeef00" ]
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
          {

            imports = [
              (import ./shared.nix {
                inherit
                  instanceName
                  clanLib
                  roles
                  config
                  lib
                  pkgs
                  ;
              })
            ];

            # Orbit external moons not declared in the inventory
            systemd.services.zerotierone.serviceConfig.ExecStartPost = lib.mkIf (settings.orbitMoons != [ ]) (
              lib.mkAfter [
                "+${pkgs.writeShellScript "orbit-external-moons" ''
                  while ! ${pkgs.netcat}/bin/nc -z localhost 9993; do
                    sleep 0.1
                  done
                  ${lib.concatMapStringsSep "\n" (moon: ''
                    zerotier-cli orbit ${moon} ${moon}
                  '') settings.orbitMoons}
                ''}"
              ]
            );
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
            systemd.services.zerotierone.serviceConfig.ExecStartPre = [
              "${pkgs.writeShellScript "init-zerotier-install-moons" ''
                mkdir -p /var/lib/zerotier-one/moons.d
                ${lib.optionalString (settings.stableEndpoints != [ ]) ''
                  if [[ ! -f /var/lib/zerotier-one/moon.json ]]; then
                    zerotier-idtool initmoon /var/lib/zerotier-one/identity.public > /var/lib/zerotier-one/moon.json
                  fi
                  ${
                    pkgs.runCommand "genmoon" { nativeBuildInputs = [ pkgs.python3 ]; } ''
                      install -Dm755 ${../../nixosModules/clanCore/zerotier/genmoon.py} $out/bin/genmoon
                      patchShebangs $out/bin/genmoon
                    ''
                  }/bin/genmoon /var/lib/zerotier-one/moon.json ${builtins.toFile "moon.json" (builtins.toJSON settings.stableEndpoints)} /var/lib/zerotier-one/moons.d
                ''}
              ''}"
            ];

            imports = [
              (import ./shared.nix {
                inherit
                  instanceName
                  clanLib
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
    description = "Manages network membership and is responsible for admitting new peers to your ZeroTier network.";
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
        options.allowedIds = lib.mkOption {
          type = lib.types.listOf lib.types.str;
          default = [ ];
          description = ''
            Extra machines by their zerotier node ID (10-char hex) that the
            controller should accept. Use this for external devices not in
            the clan inventory — the node ID is shown by `zerotier-cli info`.
          '';
          example = ''
            [ "deadbeef00" "abc1234567" ]
          '';
        };
        options.public = lib.mkOption {
          type = lib.types.bool;
          default = false;
          description = ''
            everyone can join a public network without having the administrator to accept
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
            networkId =
              config.clan.core.vars.generators."zerotier-network-${instanceName}".files.network-id.value;

            machines = lib.uniqueStrings (
              (lib.optionals (roles ? moon) (lib.attrNames roles.moon.machines))
              ++ (lib.optionals (roles ? controller) (lib.attrNames roles.controller.machines))
              ++ (lib.optionals (roles ? peer) (lib.attrNames roles.peer.machines))
            );
            networkIps = builtins.foldl' (
              ips: name:
              let
                ztIp = clanLib.getPublicValue {
                  flake = config.clan.core.settings.directory;
                  generator = "zerotier-ip-${name}-${instanceName}";
                  file = "ip";
                  default = null;
                };
              in
              if ztIp != null then ips ++ [ ztIp ] else ips
            ) [ ] machines;
            allHostIPs = settings.allowedIps ++ networkIps;

          in
          {
            imports = [
              (import ./shared.nix {
                inherit
                  instanceName
                  clanLib
                  roles
                  config
                  lib
                  pkgs
                  ;
              })
            ];
            config = {
              systemd.services.zerotierone.serviceConfig.ExecStartPre = [
                "+${pkgs.writeShellScript "init-zerotier-controller-${instanceName}" ''
                  mkdir -p /var/lib/zerotier-one/controller.d/network
                  ln -sfT ${
                    pkgs.writeText "net.json" (
                      builtins.toJSON {
                        authTokens = [ null ];
                        authorizationEndpoint = "";
                        capabilities = [ ];
                        clientId = "";
                        dns = { };
                        enableBroadcast = true;
                        id = networkId;
                        ipAssignmentPools = [ ];
                        mtu = 2800;
                        multicastLimit = 32;
                        name = instanceName;
                        uwid = networkId;
                        objtype = "network";
                        private = !settings.public;
                        remoteTraceLevel = 0;
                        remoteTraceTarget = null;
                        revision = 1;
                        routes = [ ];
                        rules = [
                          {
                            not = false;
                            "or" = false;
                            type = "ACTION_ACCEPT";
                          }
                        ];
                        rulesSource = "";
                        ssoEnabled = false;
                        tags = [ ];
                        v4AssignMode = {
                          zt = false;
                        };
                        v6AssignMode = {
                          "6plane" = false;
                          rfc4193 = true;
                          zt = false;
                        };
                      }
                    )
                  } /var/lib/zerotier-one/controller.d/network/${networkId}.json
                ''}"
              ];

              systemd.services.zerotierone.serviceConfig.ExecStartPost = [
                "+${pkgs.writeShellScript "whitelist-controller-${instanceName}" ''
                  ${config.clan.core.clanPkgs.zerotier-members}/bin/zerotier-members --network-id ${networkId} allow ${
                    builtins.substring 0 10 networkId
                  }
                ''}"
              ];

              systemd.services."zerotier-autoaccept-${instanceName}" = {
                wantedBy = [ "multi-user.target" ];
                after = [ "zerotierone.service" ];
                path = [ config.clan.core.clanPkgs.zerotierone ];
                serviceConfig.ExecStart = pkgs.writeShellScript "zerotier-autoaccept-${instanceName}" ''
                  ${lib.concatMapStringsSep "\n" (host: ''
                    ${config.clan.core.clanPkgs.zerotier-members}/bin/zerotier-members --network-id ${networkId} allow --member-ip ${host}
                  '') allHostIPs}
                  ${lib.concatMapStringsSep "\n" (id: ''
                    ${config.clan.core.clanPkgs.zerotier-members}/bin/zerotier-members --network-id ${networkId} allow ${id}
                  '') settings.allowedIds}
                '';
              };
            };

          };
      };
  };
  perMachine =
    { instances, machine, ... }:
    {
      # perMachine + perInstance
      # cannot compute in 'peer.perInstance'
      # This data is independent of the 'role'.
      # How to read this: ip's of jon in "zerotier:net-a"
      # -> Dimensions: machineName, instanceName, serviceName
      exports = lib.mapAttrs' (instanceName: _: {
        name = clanLib.buildScopeKey {
          inherit instanceName;
          machineName = machine.name;
          serviceName = config.manifest.name;
        };
        value = {
          peer.hosts = [
            {
              plain = clanLib.getPublicValue {
                generator = "zerotier-ip-${machine.name}-${instanceName}";
                file = "ip";
                flake = directory;
              };
            }
          ];
        };
      }) instances;

      nixosModule =
        {
          config,
          lib,
          pkgs,
          ...
        }:
        let
          isController = builtins.elem "controller" machine.roles;

          zerotier-tools = pkgs.callPackage ../../pkgs/zerotier-tools { };

          identity-secret =
            config.clan.core.vars.generators."zerotier-identity-${machine.name}".files.identity-secret;

          # Collect all WireGuard interface names so ZeroTier won't route through them
          wireguardInterfaceNames =
            builtins.attrNames (config.networking.wireguard.interfaces or { })
            ++ builtins.attrNames (config.networking.wg-quick.interfaces or { });

          allNetworkIds = lib.mapAttrsToList (
            instanceName: _:
            config.clan.core.vars.generators."zerotier-network-${instanceName}".files.network-id.value
          ) instances;
        in
        {
          config = {
            clan.core.vars.generators =
              # Every machine needs to define the network-id (shared) generator
              (lib.mapAttrs' (
                instanceName: instanceInfo:
                let
                  controllerName = builtins.head (builtins.attrNames instanceInfo.roles.controller.machines);
                  controllerGenerator = "zerotier-identity-${controllerName}";
                in
                lib.nameValuePair "zerotier-network-${instanceName}" {
                  share = true;
                  files.network-id.secret = false;
                  files.network-id.deploy = false;
                  runtimeInputs = [ zerotier-tools ];
                  dependencies = [ controllerGenerator ];
                  script = ''
                    zerotier-generate --mode network-id \
                      --identity-secret-file "$in/${controllerGenerator}/identity-secret" \
                      --network-id "$out/network-id"
                  '';
                }
              ) instances)
              // {
                "zerotier-identity-${machine.name}" = {
                  share = true;
                  files.identity-secret.restartUnits = [ "zerotierone.service" ];
                  runtimeInputs = [
                    config.services.zerotierone.package
                    zerotier-tools
                  ];
                  script = ''
                    zerotier-generate --mode identity-only --identity-secret "$out/identity-secret"
                  '';
                };
              }
              // (lib.mapAttrs' (
                instanceName: _:
                lib.nameValuePair "zerotier-ip-${machine.name}-${instanceName}" {
                  share = true;
                  files.ip.secret = false;
                  files.ip.deploy = false;
                  runtimeInputs = [ zerotier-tools ];
                  dependencies = [
                    "zerotier-identity-${machine.name}"
                    "zerotier-network-${instanceName}"
                  ];
                  script = ''
                    zerotier-generate --mode compute-ip \
                      --identity-secret "$in/zerotier-identity-${machine.name}/identity-secret" \
                      --network-id-file "$in/zerotier-network-${instanceName}/network-id" \
                      --ip "$out/ip"
                  '';
                }
              ) instances);

            # Override license so that we can build zerotierone without
            # having to re-import nixpkgs.
            services.zerotierone.package = lib.mkDefault (
              pkgs.callPackage ../../pkgs/zerotierone {
                includeController = isController;
              }
            );

            systemd.network.networks."09-zerotier" = {
              matchConfig.Name = "zt*";
              networkConfig = {
                LLDP = true;
                MulticastDNS = true;
                KeepConfiguration = "static";
              };
            };
            networking.firewall.allowedTCPPorts = [ 9993 ];
            networking.firewall.allowedUDPPorts = [ 9993 ];

            networking.networkmanager.unmanaged = [ "interface-name:zt*" ];
            services.zerotierone = {
              enable = true;
              joinNetworks = allNetworkIds;
            };

            # The official zerotier tcp relay no longer works: https://github.com/zerotier/ZeroTierOne/issues/2202
            # So we host our own relay in https://git.clan.lol/clan/clan-infra
            services.zerotierone.localConf.settings.tcpFallbackRelay = "65.21.12.51/4443";

            # Prevent ZeroTier from discovering/using overlay network addresses as peer
            # paths. Without this, ZT can route traffic through e.g. Yggdrasil (200::/7),
            # which itself peers over ZT, causing recursive encapsulation and intermittent
            # connectivity loss for both overlays.
            services.zerotierone.localConf.settings.interfacePrefixBlacklist = [
              "ygg" # Yggdrasil
              "hyprspace" # Hyprspace
              "tinc" # Tinc
              "tailscale" # Tailscale
              "mycelium" # Mycelium
              "wg" # WireGuard (prefix catch-all)
              "zt" # ZeroTier's own interfaces
            ]
            ++ wireguardInterfaceNames;

            systemd.services.zerotierone.serviceConfig.ExecStartPost = [
              "+${pkgs.writeShellScript "configure-interface" ''
                while ! ${pkgs.netcat}/bin/nc -z localhost 9993; do
                  sleep 0.1
                done
                zerotier-cli listnetworks -j | ${pkgs.jq}/bin/jq -r '.[] | [.portDeviceName, .name] | @tsv' \
                  | while IFS=$'\t' read -r portDeviceName name; do
                    if [[ -z "$name" ]] || [[ -z "$portDeviceName" ]]; then
                      continue
                    fi
                    ${pkgs.iproute2}/bin/ip link property add dev "$portDeviceName" altname "$name"
                done
              ''}"
            ];

            systemd.services.zerotierone.serviceConfig.ExecStartPre = [
              "+${pkgs.writeShellScript "init-zerotier-identity" ''
                mkdir -p /var/lib/zerotier-one
                if [[ ! -f /var/lib/zerotier-one/identity.secret ]]; then
                  cp ${identity-secret.path} /var/lib/zerotier-one/identity.secret
                  zerotier-idtool getpublic /var/lib/zerotier-one/identity.secret > /var/lib/zerotier-one/identity.public
                else
                  hash1=$(sha256sum /var/lib/zerotier-one/identity.secret | cut -d ' ' -f 1)
                  hash2=$(sha256sum ${identity-secret.path} | cut -d ' ' -f 1)
                  if [[ "$hash1" != "$hash2" ]]; then
                    echo "Identity secret has changed, backing up old identity"
                    cp /var/lib/zerotier-one/identity.secret /var/lib/zerotier-one/identity.secret.bac
                    cp /var/lib/zerotier-one/identity.public /var/lib/zerotier-one/identity.public.bac
                    cp ${identity-secret.path} /var/lib/zerotier-one/identity.secret
                    zerotier-idtool getpublic /var/lib/zerotier-one/identity.secret > /var/lib/zerotier-one/identity.public
                  fi
                fi
              ''}"
              "${pkgs.writeShellScript "init-zerotier-cleanup-networks" ''
                if [[ -d /var/lib/zerotier-one/networks.d ]]; then
                  find /var/lib/zerotier-one/networks.d \
                    -type f \
                    -name "*.conf" \
                    -not \( ${
                      lib.concatMapStringsSep " -o " (
                        netId: ''-name "${netId}.conf"''
                      ) config.services.zerotierone.joinNetworks
                    } \) \
                    -delete
                fi
              ''}"
            ];
          };

          imports = [
            (lib.mkIf isController {
              clan.core.state.zerotier.folders = [ "/var/lib/zerotier-one" ];
            })
          ];
        };
    };
}
