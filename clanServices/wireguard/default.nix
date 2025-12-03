/*
  There are two roles: peers and controllers:
    - Every controller has an endpoint set
    - There can be multiple peers
    - There has to be one or more controllers
    - Peers connect to ALL controllers (full mesh)
    - If only one controller exists, peers automatically use it for IP allocation
    - If multiple controllers exist, peers must specify which controller's subnet to use
    - Controllers have IPv6 forwarding enabled, every peer and controller can reach
      everyone else, via extra controller hops if necessary

    Example:
              ┌───────────────────────────────┐
              │            ◄─────────────     │
              │ controller2              controller1
              │    ▲       ─────────────►    ▲     ▲
              │    │ │ │ │                 │ │   │ │
              │    │ │ │ │                 │ │   │ │
              │    │ │ │ │                 │ │   │ │
              │    │ │ │ └───────────────┐ │ │   │ │
              │    │ │ └──────────────┐  │ │ │   │ │
              │      ▼                │  ▼ ▼     ▼
              └─► peer2               │  peer1  peer3
                                      │          ▲
                                      └──────────┘

  Network Architecture:

  IPv6 Address Allocation:
    - Base network: /40 ULA prefix (generated from instance name)
    - Controllers: Each gets a /56 subnet from the base /40
    - Peers: Each gets a unique host suffix that is used in ALL controller subnets

  Address Assignment:
    - Each peer generates a unique 64-bit host suffix (e.g., :8750:a09b:0:1)
    - This suffix is appended to each controller's /56 prefix
    - Example: peer1 with suffix :8750:a09b:0:1 gets:
      - fd51:19c1:3b:f700:8750:a09b:0:1 in controller1's subnet
      - fd51:19c1:c1:aa00:8750:a09b:0:1 in controller2's subnet

  Peers: Use a SINGLE interface that:
    - Connects to ALL controllers
    - Has multiple IPs, one in each controller's subnet (with /56 prefix)
    - Routes to each controller's /56 subnet via that controller
    - allowedIPs: Each controller's /56 subnet
    - No routing conflicts due to unique IPs per subnet

  Controllers: Use a SINGLE interface that:
    - Connects to ALL peers and ALL other controllers
    - Gets a /56 subnet from the base /40 network
    - Has IPv6 forwarding enabled for routing between peers
    - allowedIPs:
      - For peers: A /96 range containing the peer's address in this controller's subnet
      - For other controllers: The controller's /56 subnet
*/

{
  clanLib,
  ...
}:
let
  # Shared module for extraHosts configuration
  # Returns a function that takes module arguments (including _class) and returns config
  extraHostsModule =
    {
      instanceName,
      settings,
      roles,
    }:
    # This is the actual NixOS/darwin module function
    {
      _class,
      config,
      lib,
      ...
    }:
    let
      domain = if settings.domain == null then instanceName else settings.domain;
      # Controllers use their subnet's ::1 address
      controllerHosts = lib.mapAttrsToList (
        name: _value:
        let
          prefix = clanLib.getPublicValue {
            flake = config.clan.core.settings.directory;
            machine = name;
            generator = "wireguard-network-${instanceName}";
            file = "prefix";
          };
          # Controller IP is always ::1 in their subnet
          ip = prefix + "::1";
        in
        "${ip} ${name}.${domain}"
      ) roles.controller.machines;

      # Peers use their suffix in their designated controller's subnet only
      peerHosts = lib.mapAttrsToList (
        peerName: peerValue:
        let
          peerSuffix = clanLib.getPublicValue {
            flake = config.clan.core.settings.directory;
            machine = peerName;
            generator = "wireguard-network-${instanceName}";
            file = "suffix";
          };
          # Determine designated controller
          designatedController =
            if (builtins.length (builtins.attrNames roles.controller.machines) == 1) then
              (builtins.head (builtins.attrNames roles.controller.machines))
            else
              peerValue.settings.controller;
          controllerPrefix = clanLib.getPublicValue {
            flake = config.clan.core.settings.directory;
            machine = designatedController;
            generator = "wireguard-network-${instanceName}";
            file = "prefix";
          };
          peerIP = controllerPrefix + ":" + peerSuffix;
        in
        "${peerIP} ${peerName}.${domain}"
      ) roles.peer.machines;
      hostsContent = builtins.concatStringsSep "\n" (controllerHosts ++ peerHosts);
    in
    # Use conditional attribute set to avoid defining non-existent options
    # mkIf doesn't prevent option definition checks, so we must return
    # different attribute sets based on _class
    if _class == "darwin" then
      { clan.core.networking.extraHosts.wireguard = hostsContent; }
    else
      { networking.extraHosts = hostsContent; };

  # Shared interface options
  sharedInterface =
    { lib, ... }:
    {
      options.port = lib.mkOption {
        type = lib.types.int;
        example = 51820;
        default = 51820;
        description = ''
          Port for the wireguard interface
        '';
      };

      options.domain = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        defaultText = lib.literalExpression "instanceName";
        default = null;
        description = ''
          Domain suffix to use for hostnames in /etc/hosts.
          Defaults to the instance name.
        '';
      };
    };
in
{
  _class = "clan.service";
  manifest.name = "clan-core/wireguard";
  manifest.description = "Wireguard-based VPN mesh network with automatic IPv6 address allocation";
  manifest.categories = [
    "System"
    "Network"
  ];
  manifest.readme = builtins.readFile ./README.md;

  # Peer options and configuration
  roles.peer = {
    description = "A peer that connects to one or more controllers.";
    interface =
      { lib, ... }:
      {
        imports = [ sharedInterface ];

        options.controller = lib.mkOption {
          type = lib.types.str;
          example = "controller1";
          description = ''
            Machinename of the controller to attach to
          '';
        };
      };

    perInstance =
      {
        instanceName,
        settings,
        roles,
        machine,
        # mkExports,
        ...
      }:
      {

        # TODO: add exports to wireguard peers.
        # We currently only export the ip for controllers, as wireguard peer
        # have multiple IPs, one per controller and exports only allow
        # exporting one currently?

        # exports = mkExports {
        #   peer.host.plain =
        #     (clanLib.getPublicValue {
        #       flake = config.clan.core.settings.directory;
        #       machine = machine.name;
        #       generator = "wireguard-network-${instanceName}";
        #       file = "prefix";
        #     })
        #     + "::1";
        # };

        # Set default domain to instanceName

        # Peers connect to all controllers
        nixosModule =
          {
            config,
            pkgs,
            lib,
            ...
          }:
          {
            imports = [
              (extraHostsModule {
                inherit
                  instanceName
                  settings
                  roles
                  ;
              })
            ];
            # Network allocation generator for this peer - generates host suffix
            clan.core.vars.generators."wireguard-network-${instanceName}" = {
              files.suffix.secret = false;

              runtimeInputs = with pkgs; [
                python3
              ];

              # Invalidate on hostname changes
              validation.hostname = machine.name;

              script = ''
                ${pkgs.python3}/bin/python3 ${./ipv6_allocator.py} "$out" "${instanceName}" peer "${machine.name}"
              '';
            };

            # Single wireguard interface with multiple IPs
            networking.wireguard.interfaces."${instanceName}" = {
              ips =
                # Get this peer's suffix
                let
                  peerSuffix =
                    config.clan.core.vars.generators."wireguard-network-${instanceName}".files.suffix.value;
                in
                # Create an IP in each controller's subnet
                lib.mapAttrsToList (
                  ctrlName: _:
                  let
                    controllerPrefix = clanLib.getPublicValue {
                      flake = config.clan.core.settings.directory;
                      machine = ctrlName;
                      generator = "wireguard-network-${instanceName}";
                      file = "prefix";
                    };
                    peerIP = controllerPrefix + ":" + peerSuffix;
                  in
                  "${peerIP}/56"
                ) roles.controller.machines;

              privateKeyFile =
                config.clan.core.vars.generators."wireguard-keys-${instanceName}".files."privatekey".path;

              # Connect to all controllers
              peers = lib.mapAttrsToList (name: value: {
                publicKey = clanLib.getPublicValue {
                  flake = config.clan.core.settings.directory;
                  machine = name;
                  generator = "wireguard-keys-${instanceName}";
                  file = "publickey";
                };

                # Allow each controller's /56 subnet
                allowedIPs = [
                  "${
                    clanLib.getPublicValue {
                      flake = config.clan.core.settings.directory;
                      machine = name;
                      generator = "wireguard-network-${instanceName}";
                      file = "prefix";
                    }
                  }::/56"
                ];

                endpoint = "${value.settings.endpoint}:${toString value.settings.port}";

                persistentKeepalive = 25;
              }) roles.controller.machines;
            };
          };

        darwinModule =
          {
            config,
            pkgs,
            lib,
            ...
          }:
          {
            imports = [
              (extraHostsModule {
                inherit
                  instanceName
                  settings
                  roles
                  ;
              })
            ];
            # Network allocation generator for this peer - generates host suffix
            clan.core.vars.generators."wireguard-network-${instanceName}" = {
              files.suffix.secret = false;

              runtimeInputs = with pkgs; [
                python3
              ];

              # Invalidate on hostname changes
              validation.hostname = machine.name;

              script = ''
                ${pkgs.python3}/bin/python3 ${./ipv6_allocator.py} "$out" "${instanceName}" peer "${machine.name}"
              '';
            };

            # Single wireguard interface with multiple IPs using wg-quick
            networking.wg-quick.interfaces."${instanceName}" = {
              address =
                # Get this peer's suffix
                let
                  peerSuffix =
                    config.clan.core.vars.generators."wireguard-network-${instanceName}".files.suffix.value;
                in
                # Create an IP in each controller's subnet
                lib.mapAttrsToList (
                  ctrlName: _:
                  let
                    controllerPrefix = clanLib.getPublicValue {
                      flake = config.clan.core.settings.directory;
                      machine = ctrlName;
                      generator = "wireguard-network-${instanceName}";
                      file = "prefix";
                    };
                    peerIP = controllerPrefix + ":" + peerSuffix;
                  in
                  "${peerIP}/56"
                ) roles.controller.machines;

              privateKeyFile =
                config.clan.core.vars.generators."wireguard-keys-${instanceName}".files."privatekey".path;

              # Connect to all controllers
              peers = lib.mapAttrsToList (name: value: {
                publicKey = clanLib.getPublicValue {
                  flake = config.clan.core.settings.directory;
                  machine = name;
                  generator = "wireguard-keys-${instanceName}";
                  file = "publickey";
                };

                # Allow each controller's /56 subnet
                allowedIPs = [
                  "${
                    clanLib.getPublicValue {
                      flake = config.clan.core.settings.directory;
                      machine = name;
                      generator = "wireguard-network-${instanceName}";
                      file = "prefix";
                    }
                  }::/56"
                ];

                endpoint = "${value.settings.endpoint}:${toString value.settings.port}";

                persistentKeepalive = 25;
              }) roles.controller.machines;
            };
          };
      };
  };

  # Controller options and configuration
  roles.controller = {
    description = "A controller that routes peer traffic. Must be publicly reachable.";
    interface =
      { lib, ... }:
      {
        imports = [ sharedInterface ];

        options.endpoint = lib.mkOption {
          type = lib.types.str;
          example = "vpn.clan.lol";
          description = ''
            Endpoint where the controller can be reached
          '';
        };
      };
    perInstance =
      {
        settings,
        instanceName,
        roles,
        machine,
        ...
      }:
      {
        # Controllers connect to all peers and other controllers
        nixosModule =
          {
            config,
            pkgs,
            lib,
            ...
          }:
          let
            allOtherControllers = lib.filterAttrs (name: _v: name != machine.name) roles.controller.machines;
            allPeers = roles.peer.machines;
          in
          {
            imports = [
              (extraHostsModule {
                inherit
                  instanceName
                  settings
                  roles
                  ;
              })
            ];
            # Network allocation generator for this controller
            clan.core.vars.generators."wireguard-network-${instanceName}" = {
              files.prefix.secret = false;

              runtimeInputs = with pkgs; [
                python3
              ];

              # Invalidate on network or hostname changes
              validation.hostname = machine.name;

              script = ''
                ${pkgs.python3}/bin/python3 ${./ipv6_allocator.py} "$out" "${instanceName}" controller "${machine.name}"
              '';
            };

            # Enable ip forwarding, so wireguard peers can reach eachother
            boot.kernel.sysctl."net.ipv6.conf.all.forwarding" = 1;

            networking.firewall.allowedUDPPorts = [ settings.port ];

            # Single wireguard interface
            networking.wireguard.interfaces."${instanceName}" = {
              listenPort = settings.port;

              ips = [
                # Controller uses ::1 in its /56 subnet but with /40 prefix for proper routing
                "${config.clan.core.vars.generators."wireguard-network-${instanceName}".files.prefix.value}::1/40"
              ];

              privateKeyFile =
                config.clan.core.vars.generators."wireguard-keys-${instanceName}".files."privatekey".path;

              # Connect to all peers and other controllers
              peers = lib.mapAttrsToList (
                name: value:
                if allPeers ? ${name} then
                  # For peers: they now have our entire /56 subnet
                  {
                    publicKey = clanLib.getPublicValue {
                      flake = config.clan.core.settings.directory;
                      machine = name;
                      generator = "wireguard-keys-${instanceName}";
                      file = "publickey";
                    };

                    # Allow the peer's /96 range in ALL controller subnets
                    allowedIPs = lib.mapAttrsToList (
                      ctrlName: _:
                      let
                        controllerPrefix = clanLib.getPublicValue {
                          flake = config.clan.core.settings.directory;
                          machine = ctrlName;
                          generator = "wireguard-network-${instanceName}";
                          file = "prefix";
                        };
                        peerSuffix = clanLib.getPublicValue {
                          flake = config.clan.core.settings.directory;
                          machine = name;
                          generator = "wireguard-network-${instanceName}";
                          file = "suffix";
                        };
                      in
                      "${controllerPrefix}:${peerSuffix}/96"
                    ) roles.controller.machines;

                    persistentKeepalive = 25;
                  }
                else
                  # For other controllers: use their /56 subnet
                  {
                    publicKey = clanLib.getPublicValue {
                      flake = config.clan.core.settings.directory;
                      machine = name;
                      generator = "wireguard-keys-${instanceName}";
                      file = "publickey";
                    };

                    allowedIPs = [
                      "${
                        clanLib.getPublicValue {
                          flake = config.clan.core.settings.directory;
                          machine = name;
                          generator = "wireguard-network-${instanceName}";
                          file = "prefix";
                        }
                      }::/56"
                    ];

                    endpoint = "${value.settings.endpoint}:${toString value.settings.port}";
                    persistentKeepalive = 25;
                  }
              ) (allPeers // allOtherControllers);
            };
          };

        darwinModule =
          {
            config,
            pkgs,
            lib,
            ...
          }:
          let
            allOtherControllers = lib.filterAttrs (name: _v: name != machine.name) roles.controller.machines;
            allPeers = roles.peer.machines;
          in
          {
            imports = [
              (extraHostsModule {
                inherit
                  instanceName
                  settings
                  roles
                  ;
              })
            ];
            # Network allocation generator for this controller
            clan.core.vars.generators."wireguard-network-${instanceName}" = {
              files.prefix.secret = false;

              runtimeInputs = with pkgs; [
                python3
              ];

              # Invalidate on network or hostname changes
              validation.hostname = machine.name;

              script = ''
                ${pkgs.python3}/bin/python3 ${./ipv6_allocator.py} "$out" "${instanceName}" controller "${machine.name}"
              '';
            };

            # Single wireguard interface using wg-quick
            networking.wg-quick.interfaces."${instanceName}" = {
              listenPort = settings.port;

              # Enable IPv6 forwarding via postUp script, save previous value for restoration
              postUp = ''
                # Store current sysctl value in secure state directory
                state_dir="/var/lib/wireguard"
                mkdir -p "$state_dir"
                chmod 700 "$state_dir"

                # Save current IPv6 forwarding state
                sysctl -n net.inet6.ip6.forwarding > "$state_dir/${instanceName}.ip6_forwarding.state"

                # Enable IPv6 forwarding
                sysctl -w net.inet6.ip6.forwarding=1
              '';

              # Restore previous IPv6 forwarding state
              postDown = ''
                state_file="/var/lib/wireguard/${instanceName}.ip6_forwarding.state"
                if [ -f "$state_file" ]; then
                  prev_value=$(cat "$state_file")
                  sysctl -w net.inet6.ip6.forwarding="$prev_value"
                  rm -f "$state_file"
                fi
              '';

              address = [
                # Controller uses ::1 in its /56 subnet but with /40 prefix for proper routing
                "${config.clan.core.vars.generators."wireguard-network-${instanceName}".files.prefix.value}::1/40"
              ];

              privateKeyFile =
                config.clan.core.vars.generators."wireguard-keys-${instanceName}".files."privatekey".path;

              # Connect to all peers and other controllers
              peers = lib.mapAttrsToList (
                name: value:
                if allPeers ? ${name} then
                  # For peers: they now have our entire /56 subnet
                  {
                    publicKey = clanLib.getPublicValue {
                      flake = config.clan.core.settings.directory;
                      machine = name;
                      generator = "wireguard-keys-${instanceName}";
                      file = "publickey";
                    };

                    # Allow the peer's /96 range in ALL controller subnets
                    allowedIPs = lib.mapAttrsToList (
                      ctrlName: _:
                      let
                        controllerPrefix = clanLib.getPublicValue {
                          flake = config.clan.core.settings.directory;
                          machine = ctrlName;
                          generator = "wireguard-network-${instanceName}";
                          file = "prefix";
                        };
                        peerSuffix = clanLib.getPublicValue {
                          flake = config.clan.core.settings.directory;
                          machine = name;
                          generator = "wireguard-network-${instanceName}";
                          file = "suffix";
                        };
                      in
                      "${controllerPrefix}:${peerSuffix}/96"
                    ) roles.controller.machines;

                    persistentKeepalive = 25;
                  }
                else
                  # For other controllers: use their /56 subnet
                  {
                    publicKey = clanLib.getPublicValue {
                      flake = config.clan.core.settings.directory;
                      machine = name;
                      generator = "wireguard-keys-${instanceName}";
                      file = "publickey";
                    };

                    allowedIPs = [
                      "${
                        clanLib.getPublicValue {
                          flake = config.clan.core.settings.directory;
                          machine = name;
                          generator = "wireguard-network-${instanceName}";
                          file = "prefix";
                        }
                      }::/56"
                    ];

                    endpoint = "${value.settings.endpoint}:${toString value.settings.port}";
                    persistentKeepalive = 25;
                  }
              ) (allPeers // allOtherControllers);
            };
          };
      };
  };

  # Maps over all machines and produces one result per machine, regardless of role
  perMachine =
    { instances, machine, ... }:
    {
      nixosModule =
        { pkgs, lib, ... }:
        let
          # Check if this machine has conflicting roles across all instances
          machineRoleConflicts = lib.flatten (
            lib.mapAttrsToList (
              instanceName: instanceInfo:
              let
                isController =
                  instanceInfo.roles ? controller && instanceInfo.roles.controller.machines ? ${machine.name};
                isPeer = instanceInfo.roles ? peer && instanceInfo.roles.peer.machines ? ${machine.name};
              in
              lib.optional (isController && isPeer) {
                inherit instanceName;
                machineName = machine.name;
              }
            ) instances
          );
        in
        {
          # Add assertions for role conflicts
          assertions = lib.forEach machineRoleConflicts (conflict: {
            assertion = false;
            message = ''
              Machine '${conflict.machineName}' cannot have both 'controller' and 'peer' roles in the wireguard instance '${conflict.instanceName}'.
              A machine must be either a controller or a peer, not both.
            '';
          });

          # Generate keys for each instance where this machine participates
          clan.core.vars.generators = lib.mapAttrs' (
            name: _instanceInfo:
            lib.nameValuePair "wireguard-keys-${name}" {
              files.publickey.secret = false;
              files.privatekey = { };

              runtimeInputs = with pkgs; [
                wireguard-tools
              ];

              script = ''
                wg genkey > $out/privatekey
                wg pubkey < $out/privatekey > $out/publickey
              '';
            }
          ) instances;

        };

      darwinModule =
        { pkgs, lib, ... }:
        let
          # Check if this machine has conflicting roles across all instances
          machineRoleConflicts = lib.flatten (
            lib.mapAttrsToList (
              instanceName: instanceInfo:
              let
                isController =
                  instanceInfo.roles ? controller && instanceInfo.roles.controller.machines ? ${machine.name};
                isPeer = instanceInfo.roles ? peer && instanceInfo.roles.peer.machines ? ${machine.name};
              in
              lib.optional (isController && isPeer) {
                inherit instanceName;
                machineName = machine.name;
              }
            ) instances
          );
        in
        {
          # Add assertions for role conflicts
          assertions = lib.forEach machineRoleConflicts (conflict: {
            assertion = false;
            message = ''
              Machine '${conflict.machineName}' cannot have both 'controller' and 'peer' roles in the wireguard instance '${conflict.instanceName}'.
              A machine must be either a controller or a peer, not both.
            '';
          });

          # Generate keys for each instance where this machine participates
          clan.core.vars.generators = lib.mapAttrs' (
            name: _instanceInfo:
            lib.nameValuePair "wireguard-keys-${name}" {
              files.publickey.secret = false;
              files.privatekey = { };

              runtimeInputs = with pkgs; [
                wireguard-tools
              ];

              script = ''
                wg genkey > $out/privatekey
                wg pubkey < $out/privatekey > $out/publickey
              '';
            }
          ) instances;

        };
    };
}
