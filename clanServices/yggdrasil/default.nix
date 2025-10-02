{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/yggdrasil";
  manifest.description = "Yggdrasil encrypted IPv6 routing overlay network";

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

        options.peers = lib.mkOption {
          type = lib.types.listOf lib.types.str;
          default = [ ];
          description = ''
            Static peers to configure for this host.
            If not set, local peers will be auto-discovered
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
      { settings, ... }:
      {
        nixosModule =
          {
            config,
            pkgs,
            ...
          }:
          {

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
                PrivateKeyPath = "/key";
                IfName = "ygg";
                Peers = settings.peers;
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
            networking.firewall.allowedTCPPorts = [ 5400 ];
          };
      };
  };
}
