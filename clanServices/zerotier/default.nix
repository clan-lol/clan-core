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
  manifest.categories = [ "Utility" ];
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
      networking.priority = 900;
    };
  }) config.instances;

  roles.peer = {
    description = "A peer that connects to your private ZeroTier network.";
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
          peer.hosts = [
            {
              plain = clanLib.getPublicValue {
                machine = machine.name;
                generator = "zerotier";
                file = "zerotier-ip";
                flake = directory;
              };
            }
          ];
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
                      ztIp = clanLib.getPublicValue {
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
            };

          };
      };
  };
  perMachine =
    { machine, ... }:
    {
      nixosModule =
        {
          config,
          lib,
          pkgs,
          ...
        }:
        let
          cfg = config.clan.core.networking.zerotier;

          isController = builtins.elem "controller" machine.roles;
          isPeer = builtins.elem "peer" machine.roles;

          # Is only peer, excluding the controller.
          isPeerExclusive = isPeer && !isController;

          # This is slightly off, because it assumes a single instance
          # TODO: move networkId to perInstance
          networkId = config.clan.core.vars.generators.zerotier-controller.files.zerotier-network-id.value;

          # The zerotier-controller generator needs controller support to create a network,
          # even on peer-only machines (since it's a shared generator).

          zerotieroneWithController = pkgs.callPackage ../../pkgs/zerotierone {
            includeController = true;
          };

          zerotier-tools = pkgs.callPackage ../../pkgs/zerotier-tools { };
        in
        {
          options.clan.core.networking.zerotier = {
            name = lib.mkOption {
              type = lib.types.str;
              default = config.clan.core.settings.name;
              defaultText = "config.clan.core.name";
              description = ''
                zerotier network name
              '';
            };
            moon = {
              stableEndpoints = lib.mkOption {
                type = lib.types.listOf lib.types.str;
                default = [ ];
                description = ''
                  Make this machine a moon.
                  Other machines can join this moon by adding this moon in their config.
                  It will be reachable under the given stable endpoints.
                '';
                example = ''
                  [ 1.2.3.4" "10.0.0.3/9993" "2001:abcd:abcd::3/9993" ]
                '';
              };
              orbitMoons = lib.mkOption {
                type = lib.types.listOf lib.types.str;
                default = [ ];
                description = ''
                  Join these moons.
                  This machine will be able to reach all machines in these moons.
                '';
              };
            };

            controller = {
              public = lib.mkOption {
                type = lib.types.bool;
                default = false;
                description = ''
                  everyone can join a public network without having the administrator to accept
                '';
              };
            };
            settings = lib.mkOption {
              description = "override the network config in /var/lib/zerotier/bla/$network.json";
              type = lib.types.submodule { freeformType = (pkgs.formats.json { }).type; };
            };
            subnet = lib.mkOption {
              type = lib.types.nullOr lib.types.str;
              readOnly = true;
              defaultText = "Dynamically derived from 'zerotier-network-id' ";
              default =
                if networkId == null then
                  null
                else
                  let
                    part0 = builtins.substring 0 2 networkId;
                    part1 = builtins.substring 2 2 networkId;
                    part2 = builtins.substring 4 2 networkId;
                    part3 = builtins.substring 6 2 networkId;
                    part4 = builtins.substring 8 2 networkId;
                    part5 = builtins.substring 10 2 networkId;
                    part6 = builtins.substring 12 2 networkId;
                    part7 = builtins.substring 14 2 networkId;
                  in
                  "fd${part0}:${part1}${part2}:${part3}${part4}:${part5}${part6}:${part7}99:9300::/88";
              description = ''
                zerotier subnet
              '';
            };
          };
          config = lib.mkMerge [
            {
              # Override license so that we can build zerotierone without
              # having to re-import nixpkgs.
              services.zerotierone.package = lib.mkDefault (
                pkgs.callPackage ../../pkgs/zerotierone {
                  includeController = isController;
                }
              );
            }
            (
              let
                generator =
                  config.clan.core.vars.generators.zerotier or config.clan.core.vars.generators.zerotier-controller;

                zerotier-identity-secret = config.clan.core.vars.generators.zerotier.files.zerotier-identity-secret;

                # Collect all WireGuard interface names so ZeroTier won't route through them
                wireguardInterfaceNames =
                  builtins.attrNames (config.networking.wireguard.interfaces or { })
                  ++ builtins.attrNames (config.networking.wg-quick.interfaces or { });
              in
              {
                environment.etc."zerotier/ip".text = generator.files.zerotier-ip.value;

                systemd.network.networks."09-zerotier" = {
                  matchConfig.Name = "zt*";
                  networkConfig = {
                    LLDP = true;
                    MulticastDNS = true;
                    KeepConfiguration = "static";
                  };
                };

                systemd.services.zerotierone.serviceConfig.ExecStartPre = [
                  "+${pkgs.writeShellScript "init-zerotier" ''
                    # compare hashes of the current identity secret and the one in the config
                    hash1=$(sha256sum /var/lib/zerotier-one/identity.secret | cut -d ' ' -f 1)
                    hash2=$(sha256sum ${zerotier-identity-secret.path} | cut -d ' ' -f 1)
                    if [[ "$hash1" != "$hash2" ]]; then
                      echo "Identity secret has changed, backing up old identity to /var/lib/zerotier-one/identity.secret.bac"
                      cp /var/lib/zerotier-one/identity.secret /var/lib/zerotier-one/identity.secret.bac
                      cp /var/lib/zerotier-one/identity.public /var/lib/zerotier-one/identity.public.bac
                      cp ${zerotier-identity-secret.path} /var/lib/zerotier-one/identity.secret
                      zerotier-idtool getpublic /var/lib/zerotier-one/identity.secret > /var/lib/zerotier-one/identity.public
                    fi

                    ${lib.optionalString isController ''
                      mkdir -p /var/lib/zerotier-one/controller.d/network
                      ln -sfT ${pkgs.writeText "net.json" (builtins.toJSON cfg.settings)} /var/lib/zerotier-one/controller.d/network/${networkId}.json
                    ''}
                    ${lib.optionalString (cfg.moon.stableEndpoints != [ ]) ''
                      if [[ ! -f /var/lib/zerotier-one/moon.json ]]; then
                        zerotier-idtool initmoon /var/lib/zerotier-one/identity.public > /var/lib/zerotier-one/moon.json
                      fi
                      ${
                        pkgs.runCommand "genmoon" { nativeBuildInputs = [ pkgs.python3 ]; } ''
                          install -Dm755 ${../../nixosModules/clanCore/zerotier/genmoon.py} $out/bin/genmoon
                          patchShebangs $out/bin/genmoon
                        ''
                      }/bin/genmoon /var/lib/zerotier-one/moon.json ${builtins.toFile "moon.json" (builtins.toJSON cfg.moon.stableEndpoints)} /var/lib/zerotier-one/moons.d
                    ''}

                    # cleanup old networks
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
                        # Execute the command for each element
                        ${pkgs.iproute2}/bin/ip link property add dev "$portDeviceName" altname "$name"
                    done

                    ${lib.concatMapStringsSep "\n" (moon: ''
                      zerotier-cli orbit ${moon} ${moon}
                    '') cfg.moon.orbitMoons}
                  ''}"
                ];

                networking.firewall.allowedTCPPorts = [ 9993 ]; # zerotier
                networking.firewall.allowedUDPPorts = [ 9993 ]; # zerotier

                networking.networkmanager.unmanaged = [ "interface-name:zt*" ];

                services.zerotierone = {
                  enable = true;
                  joinNetworks = [ networkId ];
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
              }
            )

            (lib.mkIf isController {
              clan.core.state.zerotier.folders = [ "/var/lib/zerotier-one" ];

            })
            {
              # only the controller needs to have the key in the repo, the other clients can be dynamic
              # we generate the zerotier code manually for the controller, since it's part of the bootstrap command
              clan.core.vars.generators.zerotier-controller = {
                share = true;

                files.zerotier-ip.secret = false;
                files.zerotier-ip.restartUnits = [ "zerotierone.service" ];

                files.zerotier-network-id.secret = false;
                files.zerotier-network-id.restartUnits = [ "zerotierone.service" ];

                # No machine has access to this
                # This gets copied only to the private generator later via dependencies
                files.zerotier-identity-secret.deploy = false;

                runtimeInputs = [
                  zerotieroneWithController
                  zerotier-tools
                ];
                script = ''
                  source ${(pkgs.callPackage ../../pkgs/minifakeroot { })}/share/minifakeroot/rc
                  zerotier-generate --mode network \
                    --ip "$out/zerotier-ip" \
                    --identity-secret "$out/zerotier-identity-secret" \
                    --network-id "$out/zerotier-network-id"
                '';
              };
            }

            (lib.mkIf isController {
              # Copies the outputs of "zerotier-controller" into a per-machine generator
              # This allows "deploy=true" which is required only for the controller
              clan.core.vars.generators.zerotier = {
                files.zerotier-ip.secret = false;
                files.zerotier-ip.restartUnits = [ "zerotierone.service" ];

                files.zerotier-network-id.secret = false;
                files.zerotier-network-id.restartUnits = [ "zerotierone.service" ];

                # No machine has access to this
                # This gets copied only to the private generator later via dependencies
                files.zerotier-identity-secret.restartUnits = [ "zerotierone.service" ];

                dependencies = [ "zerotier-controller" ];
                script = ''
                  cp $in/zerotier-controller/zerotier-ip $out/zerotier-ip
                  cp $in/zerotier-controller/zerotier-network-id $out/zerotier-network-id
                  cp $in/zerotier-controller/zerotier-identity-secret $out/zerotier-identity-secret
                '';
              };
            })
            (lib.mkIf isPeerExclusive {
              # This generator only exists on pure peers
              clan.core.vars.generators.zerotier = {
                files.zerotier-ip.secret = false;
                files.zerotier-ip.restartUnits = [ "zerotierone.service" ];
                files.zerotier-identity-secret = {
                  restartUnits = [ "zerotierone.service" ];
                };
                runtimeInputs = [
                  config.services.zerotierone.package
                  zerotier-tools
                ];
                dependencies = [ "zerotier-controller" ];
                script = ''
                  zerotier-generate --mode identity \
                    --ip "$out/zerotier-ip" \
                    --identity-secret "$out/zerotier-identity-secret" \
                    --network-id-file $in/zerotier-controller/zerotier-network-id
                '';
              };

              clan.core.networking.targetHost = lib.mkDefault "root@[${config.clan.core.vars.generators.zerotier.files.zerotier-ip.value}]";
            })
            (lib.mkIf isController {
              clan.core.networking.zerotier.settings = {
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
                name = cfg.name;
                uwid = networkId;
                objtype = "network";
                private = !cfg.controller.public;
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
              };

              environment.etc."zerotier/network-id".text = networkId;
              environment.systemPackages = [ config.clan.core.clanPkgs.zerotier-members ];
              systemd.services.zerotierone.serviceConfig.ExecStartPost = [
                "+${pkgs.writeShellScript "whitelist-controller" ''
                  ${config.clan.core.clanPkgs.zerotier-members}/bin/zerotier-members allow ${
                    builtins.substring 0 10 networkId
                  }
                ''}"
              ];
            })
          ];
        };
    };
}
