{
  directory,
  lib,
  clanLib,
  config,
  ...
}:
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
                # We need to add [ ] for ipv6 addresses
                if (lib.hasInfix ":" ip) then
                  [
                    # "tcp://[${ip}]:6443"
                    "quic://[${ip}]:6443"
                    "ws://[${ip}]:6443"
                    "tls://[${ip}]:6443"
                  ]
                else
                  [
                    # "tcp://[${ip}]:6443"
                    "quic://${ip}:6443"
                    "ws://${ip}:6443"
                    "tls://${ip}:6443"
                  ]
              ) filteredHosts;

            # Filter out exports from the local machine and yggdrasil
            # exports to avoid self-connections
            nonLocalExports = lib.filterAttrs (
              name: _:
              let
                parts = lib.splitString ":" name;
                exportMachineName = lib.last parts;
              in
              # Exclude yggdrasil exports and exports from this
              # machine. Self-connections lead to ErrBadKey!
              !(lib.hasPrefix "clan-core/yggdrasil" name) && exportMachineName != machine.name
            ) exports;

            # TODO make it nicer @lassulus, @picnoir wants microlens
            exportedPeerIPs = lib.flatten (map mkPeers (lib.attrValues nonLocalExports));

            exportedPeers = exportedPeerIPs;

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
                  ip
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
              ];

              script = ''
                # Generate private key
                openssl genpkey -algorithm Ed25519 -out $out/privateKey

                # Generate corresponding public key
                openssl pkey -in $out/privateKey -pubout -out $out/publicKey

                # Derive IPv6 address from key
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
                  "quic://[::]:6443"
                  "ws://[::]:6443"
                  "tls://[::]:6443"
                ];
                PrivateKeyPath = "/key";
                IfName = "ygg";
                Peers = lib.lists.unique (exportedPeers ++ settings.extraPeers);
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
                6443
                9001
              ];
              allowedTCPPorts = [
                5400
                6443
              ];
            };
          };
      };
  };
}
