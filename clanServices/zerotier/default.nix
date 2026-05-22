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
        roles,
        mkExports,
        machine,
        settings,
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
          let
            isController = builtins.elem "controller" machine.roles;
            zerotier-tools = pkgs.callPackage ../../pkgs/zerotier-tools { };
          in
          {
            # This generator only exists on pure peers
            # !!! Attention: The controller defines a generator with the same name
            # If the machine is a controller; we disable this generator
            clan.core.vars.generators.zerotier = lib.mkIf (!isController) {
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

            imports = [
              (import ./shared.nix {
                inherit
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
            # FIXME: This would return the same ID for all networks currently
            networkId = config.clan.core.vars.generators.zerotier-controller.files.zerotier-network-id.value;
          in
          {
            imports = [
              (import ./shared.nix {
                inherit
                  clanLib
                  roles
                  config
                  lib
                  pkgs
                  ;
              })
            ];
            config = {
              # Copies the outputs of "zerotier-controller" into a per-machine generator
              # This allows "deploy=true" which is required only for the controller
              # !!! Attention: uses the same generator name as every peer.
              # Peers need to check to avoid defining the same generator
              clan.core.vars.generators.zerotier = {
                files.zerotier-ip.secret = false;
                files.zerotier-ip.restartUnits = [ "zerotierone.service" ];

                files.zerotier-network-id.secret = false;
                files.zerotier-network-id.restartUnits = [ "zerotierone.servqice" ];

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
              environment.etc."zerotier/network-id".text = networkId;

              systemd.services.zerotierone.serviceConfig.ExecStartPre = [
                "+${pkgs.writeShellScript "init-zerotier-01-controller" ''
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
                "+${pkgs.writeShellScript "whitelist-controller" ''
                  ${config.clan.core.clanPkgs.zerotier-members}/bin/zerotier-members allow ${
                    builtins.substring 0 10 networkId
                  }
                ''}"
              ];

              systemd.services.zerotier-inventory-autoaccept =
                let
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
          isController = builtins.elem "controller" machine.roles;
          isPeer = builtins.elem "peer" machine.roles;

          # Is only peer, excluding the controller.
          isPeerExclusive = isPeer && !isController;

          # This is slightly off, because it assumes a single instance
          # TODO: move networkId to perInstance
          networkId = config.clan.core.vars.generators.zerotier-controller.files.zerotier-network-id.value;

          zerotier-tools = pkgs.callPackage ../../pkgs/zerotier-tools { };

          zerotier-identity-secret = config.clan.core.vars.generators.zerotier.files.zerotier-identity-secret;

          # Collect all WireGuard interface names so ZeroTier won't route through them
          wireguardInterfaceNames =
            builtins.attrNames (config.networking.wireguard.interfaces or { })
            ++ builtins.attrNames (config.networking.wg-quick.interfaces or { });
        in
        {
          # once perMachine
          config = {
            # Override license so that we can build zerotierone without
            # having to re-import nixpkgs.
            services.zerotierone.package = lib.mkDefault (
              pkgs.callPackage ../../pkgs/zerotierone {
                includeController = isController;
              }
            );

            # Script to accept new members on the fly
            environment.systemPackages = [ config.clan.core.clanPkgs.zerotier-members ];

            systemd.network.networks."09-zerotier" = {
              matchConfig.Name = "zt*";
              networkConfig = {
                LLDP = true;
                MulticastDNS = true;
                KeepConfiguration = "static";
              };
            };
            networking.firewall.allowedTCPPorts = [ 9993 ]; # zerotier
            networking.firewall.allowedUDPPorts = [ 9993 ]; # zerotier

            networking.networkmanager.unmanaged = [ "interface-name:zt*" ];
            services.zerotierone = {
              enable = true;
              # TODO: Collect from all instances once vars migration happens
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
              ''}"
            ];
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
                config.clan.core.clanPkgs.zerotierone
                zerotier-tools
              ];
              script = ''
                zerotier-generate --mode network \
                  --ip "$out/zerotier-ip" \
                  --identity-secret "$out/zerotier-identity-secret" \
                  --network-id "$out/zerotier-network-id"
              '';
            };
            systemd.services.zerotierone.serviceConfig.ExecStartPre = [
              "+${pkgs.writeShellScript "init-zerotier-identity" ''
                mkdir -p /var/lib/zerotier-one
                if [[ ! -f /var/lib/zerotier-one/identity.secret ]]; then
                  cp ${zerotier-identity-secret.path} /var/lib/zerotier-one/identity.secret
                  zerotier-idtool getpublic /var/lib/zerotier-one/identity.secret > /var/lib/zerotier-one/identity.public
                else
                  hash1=$(sha256sum /var/lib/zerotier-one/identity.secret | cut -d ' ' -f 1)
                  hash2=$(sha256sum ${zerotier-identity-secret.path} | cut -d ' ' -f 1)
                  if [[ "$hash1" != "$hash2" ]]; then
                    echo "Identity secret has changed, backing up old identity"
                    cp /var/lib/zerotier-one/identity.secret /var/lib/zerotier-one/identity.secret.bac
                    cp /var/lib/zerotier-one/identity.public /var/lib/zerotier-one/identity.public.bac
                    cp ${zerotier-identity-secret.path} /var/lib/zerotier-one/identity.secret
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
            (lib.mkIf isPeerExclusive {
              clan.core.networking.targetHost = lib.mkDefault "root@[${config.clan.core.vars.generators.zerotier.files.zerotier-ip.value}]";
            })
          ];
        };
    };
}
