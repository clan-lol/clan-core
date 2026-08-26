{
  directory,
  lib,
  clanLib,
  config,
  ...
}@service:
{
  _class = "clan.service";
  manifest.name = "clan-core/yggdrasil";
  manifest.description = "Yggdrasil encrypted IPv6 routing overlay network";
  manifest.categories = [ "Network" ];
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
      networking.priority = 2000;
    };
  }) config.instances;

  roles.default = {
    description = "Placeholder role to apply the yggdrasil service";
    interface =
      { lib, ... }:
      {
        options.multicastInterfaces = lib.mkOption {
          type = lib.types.listOf lib.types.attrs;
          default = [
            {
              # Degrade overlay/VPN interfaces so direct links win.
              Regex = "(zt|wg|tailscale|mycelium|tinc|tun|tap|ygg).*";
              Beacon = true;
              Listen = true;
              Port = 5400;
              Priority = 10;
            }
            {
              Regex = ".*";
              Beacon = true;
              Listen = true;
              Port = 5400;
            }
          ];
          description = ''
            Interfaces for Yggdrasil multicast peer discovery; enabled on
            all interfaces by default, `[ ]` disables. Listener ports are
            opened in the firewall automatically.
            See https://yggdrasil-network.github.io/configurationref.html#multicastinterfaces
          '';
          example = [
            {
              # Restrict to only VPN interfaces
              Regex = "(wg|zt|tailscale|mycelium|tinc|tun|tap).*";
              Beacon = true;
              Listen = true;
              Port = 5400;
              Priority = 0;
            }
            {
              # Or restrict to ethernet interfaces
              Regex = "(eth|en).*";
              Beacon = true;
              Listen = true;
              Port = 5400;
              Priority = 100;
            }
            {
              # Or restrict to wifi interfaces
              Regex = "(wl).*";
              Beacon = true;
              Listen = true;
              Port = 5400;
              Priority = 101;
            }
          ];
        };

        # Ports
        options.ports = lib.mkOption {
          description = "Port configuration for Yggdrasil listeners.";
          default = { };
          type = lib.types.submodule {
            options = {
              tcp = lib.mkOption {
                description = "TCP port, used for the tcp:// yggdrasil listener";
                default = 6443;
                type = lib.types.port;
              };

              quic = lib.mkOption {
                description = "QUIC port, used for the quic:// yggdrasil listener. Disabled by default.";
                default = null;
                type = lib.types.nullOr lib.types.port;
              };

              ws = lib.mkOption {
                description = "Websocket port, used for the ws:// yggdrasil listener. Disabled by default.";
                default = null;
                type = lib.types.nullOr lib.types.port;
              };

              tls = lib.mkOption {
                description = "TLS port, used for the tls:// yggdrasil listener";
                default = 6446;
                type = lib.types.port;
              };
            };
          };
        };

        options.extraPeers = lib.mkOption {
          type = lib.types.listOf lib.types.str;
          default = [ ];
          description = ''
            Additional static peers to configure for this host. If you use a
            VPN clan service, it will automatically be added as peers to other hosts.
            Local peers are also auto-discovered and don't need to be added.
          '';
          example = [
            "tcp://192.168.1.1:6443"
            "tls://192.168.1.1:6446"
          ];
        };

        options.extraYggdrasilIPs = lib.mkOption {
          type = lib.types.listOf lib.types.str;
          default = [ ];
          description = ''
            Allow IPs to be able to connect to this host other than Clan members. By default,
            this service only allows clan members to connect to each other. Using this option
            to allow the host to connect to external Yggdrasil IP addresses.
          '';
          example = [ "324:71e:281a:9ed3::cafe" ];
        };
      };
    perInstance =
      {
        settings,
        roles,
        mkExports,
        exports,
        machine,
        ...
      }:
      {

        exports = mkExports {
          peer.hosts = [
            {
              plain = clanLib.getPublicValue {
                machine = machine.name;
                generator = "yggdrasil";
                file = "address";
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
          let

            # Build peer URLs for one export, dialing the given protocols
            # for each IP.
            mkPeers =
              protocols: export:
              let
                # Extract host list from the export
                hostList = export.peer.hosts or [ ];

                # Extract actual IP values from tagged unions
                extractHostValue =
                  hostItem:
                  if hostItem ? plain then
                    hostItem.plain
                  else if hostItem ? var then
                    clanLib.getPublicValue (hostItem.var // { default = ""; })
                  else
                    throw "Unknown host type in export";

                # Get list of IP addresses and strip whitespace (newlines, etc.)
                hosts = map (ip: lib.trim (extractHostValue ip)) hostList;

                # Filter out empty IPs
                filteredHosts = lib.filter (ip: ip != "") hosts;

                # Static peers get a worse (higher) priority than
                # multicast-discovered links, so local peerings carry the
                # traffic and static routes act as fallback.
                staticPeerParams = "?priority=20";
                mkPeerUrlsForIp =
                  ip:
                  if (lib.hasSuffix ".onion" ip) then
                    # Tor onion peers use the local SOCKS proxy
                    [ "socks://127.0.0.1:9050/${ip}:${toString settings.ports.tcp}${staticPeerParams}" ]
                  else
                    map (
                      protocol:
                      let
                        port = toString settings.ports.${protocol};
                        # We need to add [ ] for IPv6 addresses
                        host = if (lib.hasInfix ":" ip) then "[${ip}]" else ip;
                      in
                      "${protocol}://${host}:${port}${staticPeerParams}"
                    ) protocols;
              in
              lib.concatMap mkPeerUrlsForIp filteredHosts;

            # Filter out exports from the local machine and yggdrasil
            # exports to avoid self-connections
            nonLocalExports = clanLib.selectExports (
              scope: scope.serviceName != service.config.manifest.name && scope.machineName != machine.name
            ) exports;

            # A single tcp:// link suffices for exports from VPN transports
            # (already encrypted, unfiltered). Internet exports may cross
            # filtered networks, so dial every enabled protocol to maximize
            # the chance that one gets through.
            enabledProtocols = lib.attrNames (lib.filterAttrs (_: port: port != null) settings.ports);
            exportedPeers = lib.concatLists (
              lib.mapAttrsToList (
                scopeKey: export:
                mkPeers (
                  if (clanLib.parseScope scopeKey).serviceName == "clan-core/internet" then
                    enabledProtocols
                  else
                    [ "tcp" ]
                ) export
              ) nonLocalExports
            );

            # Collect public keys from all machines in the role
            allowedPublicKeys = lib.filter (key: key != "") (
              map (
                name:
                lib.trim (
                  clanLib.getPublicValue {
                    flake = config.clan.core.settings.directory;
                    machine = name;
                    generator = "yggdrasil";
                    file = "publicKey";
                    default = "";
                  }
                )
              ) (lib.attrNames roles.default.machines)
            );

            # Collect Yggdrasil IPv6 addresses from all machines in the role
            allowedYggdrasilIPs =
              lib.filter (ip: ip != "") (
                map (
                  name:
                  lib.trim (
                    clanLib.getPublicValue {
                      flake = config.clan.core.settings.directory;
                      machine = name;
                      generator = "yggdrasil";
                      file = "address";
                      default = "";
                    }
                  )
                ) (lib.attrNames roles.default.machines)
              )
              ++ settings.extraYggdrasilIPs;

          in
          {

            # Advertise this machine's yggdrasil address so clan-internal
            # services (via dm-dns) bind only to VPN interfaces.
            clan.core.networking.internalListenAddresses = [
              (clanLib.getPublicValue {
                flake = config.clan.core.settings.directory;
                machine = machine.name;
                generator = "yggdrasil";
                file = "address";
                default = "";
              })
            ];

            # Set <yggdrasil ip> <hostname>.<domain> for all hosts.
            # Networking modules will then add themselves as peers, so we can
            # always use this to resolve a host via the best possible route,
            # doing fail-over if needed.
            networking.extraHosts = lib.concatStringsSep "\n" (
              lib.filter (n: n != "") (
                map (
                  name:
                  let
                    ip = clanLib.getPublicValue {
                      flake = config.clan.core.settings.directory;
                      machine = name;
                      generator = "yggdrasil";
                      file = "address";
                      default = "";
                    };
                  in
                  "${ip} ${name}.${config.clan.core.settings.domain}"
                ) (lib.attrNames roles.default.machines)
              )
            );

            clan.core.vars.generators.yggdrasil = {

              files.privateKey = { };
              files.publicKey.secret = false;
              files.address.secret = false;

              runtimeInputs = with pkgs; [
                yggdrasil
                jq
                openssl
                xxd
              ];

              script = ''
                # Generate private key
                openssl genpkey -algorithm Ed25519 -out $out/privateKey

                # Extract raw 32-byte public key and convert to hex.
                # The DER format has a 12-byte header, skip it to get the raw
                # key bytes
                openssl pkey -in $out/privateKey -pubout -outform DER | \
                  tail -c +13 | xxd -p -c 64 | tr -d '\n' > $out/publicKey

                # Derive IPv6 address from key
                echo "{\"PrivateKeyPath\": \"$out/privateKey\"}" | \
                  yggdrasil -useconf -address | tr -d '\n' > $out/address
              '';
            };

            # TODO remove this on next nixpkgs bump and use the secret key file directly
            # Set up credential loading ourselves to work with both old and new nixpkgs modules
            # Use mkForce to override any nixpkgs-set LoadCredential (new module adds its own)
            systemd.services.yggdrasil.serviceConfig.LoadCredential =
              lib.mkForce "private-key:${config.clan.core.vars.generators.yggdrasil.files.privateKey.path}";
            systemd.services.yggdrasil.serviceConfig.BindReadOnlyPaths = lib.mkForce [
              "%d/private-key:/private-key"
            ];

            services.yggdrasil = {
              enable = true;
              openMulticastPort = true;
              # We persist our keys with vars.
              persistentKeys = false;
              settings = {
                Listen = lib.mapAttrsToList (protocol: port: "${protocol}://[::]:${toString port}") (
                  lib.filterAttrs (_: port: port != null) settings.ports
                );
                # Point to the credential-mounted path (works with both old and new modules)
                PrivateKeyPath = "/private-key";
                IfName = "ygg";
                Peers = lib.uniqueStrings (exportedPeers ++ settings.extraPeers);
                AllowedEncryptionPublicKeys = allowedPublicKeys;
                NodeInfoPrivacy = true;
                MulticastInterfaces = settings.multicastInterfaces;
              };
            };
            networking.firewall = with settings.ports; {
              allowedUDPPorts = lib.optional (quic != null) quic;
              allowedTCPPorts = [
                tcp
                tls # TLS
              ]
              ++ lib.optional (ws != null) ws
              # Link-local TCP listener ports for multicast peer discovery
              ++ lib.unique (
                lib.concatMap (
                  mi: lib.optional ((mi.Listen or false) && (mi.Port or 0) != 0) mi.Port
                ) settings.multicastInterfaces
              );

              # Restrict ygg interface to only allow traffic from clan members
              # (iptables)
              extraCommands = lib.mkIf (!config.networking.nftables.enable) ''
                # Create chain for yggdrasil input filtering
                ip6tables -N ygg-input 2>/dev/null || true
                ip6tables -F ygg-input

                # Allow traffic from clan member IPs to continue to port-based firewall rules
                ${lib.concatMapStringsSep "\n    " (
                  ip: "ip6tables -A ygg-input -s ${lib.escapeShellArg ip} -i ygg -j RETURN"
                ) allowedYggdrasilIPs}

                # Drop all other traffic on ygg interface
                ip6tables -A ygg-input -i ygg -j DROP

                # Insert rule at beginning of INPUT chain
                ip6tables -I INPUT -i ygg -j ygg-input
              '';

              extraStopCommands = lib.mkIf (!config.networking.nftables.enable) ''
                # Remove yggdrasil chain on firewall stop
                ip6tables -D INPUT -i ygg -j ygg-input 2>/dev/null || true
                ip6tables -F ygg-input 2>/dev/null || true
                ip6tables -X ygg-input 2>/dev/null || true
              '';
            };

            # Restrict ygg interface to only allow traffic from clan members
            # (nftables)
            networking.nftables.tables.yggdrasil-filter = lib.mkIf config.networking.nftables.enable {
              family = "ip6";
              content = ''
                chain input {
                  type filter hook input priority -10; policy accept;

                  # Only apply to ygg interface
                  iifname "ygg" ip6 saddr {
                    ${lib.concatMapStringsSep ",\n        " (ip: "${ip}") allowedYggdrasilIPs}
                  } counter return comment "allow clan yggdrasil IPs to continue to port-based firewall"

                  # Drop all other traffic on ygg interface
                  iifname "ygg" counter drop comment "block non-clan yggdrasil traffic"
                }
              '';
            };
          };
      };
  };
}
