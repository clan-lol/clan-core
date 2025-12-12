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
  manifest.readme = builtins.readFile ./README.md;

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
        options.extraMulticastInterfaces = lib.mkOption {
          type = lib.types.listOf lib.types.attrs;
          default = [ ];
          description = ''
            Additional interfaces to use for Multicast. See
            https://yggdrasil-network.github.io/configurationref.html#multicastinterfaces
            for reference.
          '';
          example = [
            {
              Regex = "(wg).*";
              Beacon = true;
              Listen = true;
              Port = 5400;
              Priority = 1020;
            }
          ];
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
            "quic://192.168.1.1:6443"
            "tls://192.168.1.1:6443"
            "ws://192.168.1.1:6443"
          ];
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

            mkPeers =
              export:
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
                hosts = map (ip: lib.strings.trim (extractHostValue ip)) hostList;

                # Filter out empty IPs
                filteredHosts = lib.filter (ip: ip != "") hosts;
              in
              lib.concatMap (
                ip:
                if (lib.hasSuffix ".onion" ip) then
                  [
                    # Tor onion peers use SOCKS proxy
                    # socks:// = TCP (port 6443)
                    # sockstls:// = TLS (port 6446)
                    "socks://127.0.0.1:9050/${ip}:6443"
                    "sockstls://127.0.0.1:9050/${ip}:6446"
                  ]
                else if (lib.hasInfix ":" ip) then
                  [
                    # We need to add [ ] for IPv6 addresses
                    "tcp://[${ip}]:6443"
                    "quic://[${ip}]:6444"
                    "ws://[${ip}]:6445"
                    "tls://[${ip}]:6446"
                  ]
                else
                  [
                    # No [ ] for IPv4 addresses
                    "tcp://${ip}:6443"
                    "quic://${ip}:6444"
                    "ws://${ip}:6445"
                    "tls://${ip}:6446"
                  ]
              ) filteredHosts;

            # Filter out exports from the local machine and yggdrasil
            # exports to avoid self-connections
            nonLocalExports = clanLib.selectExports (
              scope: scope.serviceName != service.config.manifest.name && scope.machineName != machine.name
            ) exports;

            # TODO make it nicer @lassulus, @picnoir wants microlens
            exportedPeerIPs = lib.concatLists (map mkPeers (lib.attrValues nonLocalExports));

            exportedPeers = exportedPeerIPs;

            # Read this machine's own public key
            localPublicKey = lib.strings.trim (
              builtins.readFile config.clan.core.vars.generators.yggdrasil.files.publicKey.path
            );

            # Collect public keys from all machines in the role (including self)
            allowedPublicKeys = lib.lists.unique (
              lib.filter (key: key != "") (
                [ localPublicKey ] ++
                map (
                  name:
                  lib.strings.trim (
                    clanLib.getPublicValue {
                      flake = config.clan.core.settings.directory;
                      machine = name;
                      generator = "yggdrasil";
                      file = "publicKey";
                      default = "";
                    }
                  )
                ) (lib.attrNames roles.default.machines)
              )
            );

          in
          {

            # Set <yggdrasil ip> <hostname>.<domain> for all hosts.
            # Networking modules will then add themselves as peers, so we can
            # always use this to resolve a host via the best possible route,
            # doing fail-over if needed.
            networking.extraHosts = lib.strings.concatStringsSep "\n" (
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
                # Generate private key (only if it doesn't exist - handled by clan vars)
                openssl genpkey -algorithm Ed25519 -out $out/privateKey

                # Extract raw 32-byte public key and convert to hex
                # The DER format has a 12-byte header, skip it to get the raw key bytes
                openssl pkey -in $out/privateKey -pubout -outform DER | \
                  tail -c +13 | xxd -p -c 64 | tr -d '\n' > $out/publicKey

                # Derive IPv6 address from key (unchanged)
                echo "{\"PrivateKeyPath\": \"$out/privateKey\"}" | yggdrasil -useconf -address | tr -d '\n' > $out/address
              '';
            };

            systemd.services.yggdrasil.serviceConfig.BindReadOnlyPaths = [
              "%d/key:/key"
            ];

            systemd.services.yggdrasil.serviceConfig.LoadCredential =
              "key:${config.clan.core.vars.generators.yggdrasil.files.privateKey.path}";

            services.yggdrasil = {
              enable = true;
              openMulticastPort = true;
              # We don't need this option, because we persist our keys with
              # vars by ourselves. This option creates an unnecesary additional
              # systemd service to save/load the keys and should be removed
              # from the NixOS module entirely, as it can be replaced by the
              # (at the time of writing undocumented) PrivateKeyPath= setting.
              # See https://github.com/NixOS/nixpkgs/pull/440910#issuecomment-3301835895 for details.
              persistentKeys = false;
              settings = {
                Listen = [
                  "tcp://[::]:6443"
                  "quic://[::]:6444"
                  "ws://[::]:6445"
                  "tls://[::]:6446"
                ];
                PrivateKeyPath = "/key";
                IfName = "ygg";
                Peers = lib.lists.uniqueStrings (exportedPeers ++ settings.extraPeers);
                AllowedEncryptionPublicKeys = allowedPublicKeys;
                MulticastInterfaces = [
                  # Ethernet is preferred over WIFI
                  {
                    Regex = "(eth|en).*";
                    Beacon = true;
                    Listen = true;
                    Port = 5400;
                    Priority = 1024;
                  }
                  {
                    Regex = "(wl).*";
                    Beacon = true;
                    Listen = true;
                    Port = 5400;
                    Priority = 1025;
                  }
                ]
                ++ settings.extraMulticastInterfaces;
              };
            };
            networking.firewall = {
              allowedUDPPorts = [
                5400 # Multicast
                6444 # QUIC
              ];
              allowedTCPPorts = [
                6443 # TCP
                6445 # WebSocket
                6446 # TLS
              ];
            };
          };
      };
  };
}
