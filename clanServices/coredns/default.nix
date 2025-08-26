{ ... }:
{
  _class = "clan.service";
  manifest.name = "coredns";
  manifest.description = "Clan-internal DNS and service exposure";
  manifest.categories = [ "Network" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.server = {

    interface =
      { lib, ... }:
      {
        options.tld = lib.mkOption {
          type = lib.types.str;
          default = "clan";
          description = ''
            Top-level domain for this instance. All services below this will be
            resolved internally.
          '';
        };

        options.ip = lib.mkOption {
          type = lib.types.str;
          # TODO: Set a default
          description = "IP for the DNS to listen on";
        };
      };

    perInstance =
      {
        roles,
        settings,
        ...
      }:
      {
        nixosModule =
          {
            lib,
            pkgs,
            ...
          }:
          {

            networking.firewall.allowedTCPPorts = [ 53 ];
            networking.firewall.allowedUDPPorts = [ 53 ];

            services.coredns =
              let

                # Get all service entries for one host
                hostServiceEntries =
                  host:
                  lib.strings.concatStringsSep "\n" (
                    map (
                      service: "${service} IN A ${roles.default.machines.${host}.settings.ip}   ; ${host}"
                    ) roles.default.machines.${host}.settings.services
                  );

                zonefile = pkgs.writeTextFile {
                  name = "db.${settings.tld}";
                  text = ''
                    $TTL 3600
                    @   IN SOA  ns.${settings.tld}. admin.${settings.tld}. 1 7200 3600 1209600 3600
                        IN NS   ns.${settings.tld}.
                    ns  IN A    ${settings.ip}   ; DNS server

                  ''
                  + (lib.strings.concatStringsSep "\n" (
                    map (host: hostServiceEntries host) (lib.attrNames roles.default.machines)
                  ));
                };

              in
              {
                enable = true;
                config = ''
                  . {
                      forward . 1.1.1.1
                      cache 30
                  }

                  ${settings.tld} {
                      file ${zonefile}
                  }
                '';
              };
          };
      };
  };

  roles.default = {
    interface =
      { lib, ... }:
      {
        options.services = lib.mkOption {
          type = lib.types.listOf lib.types.str;
          default = [ ];
          description = ''
            Service endpoints this host exposes (without TLD). Each entry will
            be resolved to <entry>.<tld> using the configured top-level domain.
          '';
        };

        options.ip = lib.mkOption {
          type = lib.types.str;
          # TODO: Set a default
          description = "IP on which the services will listen";
        };
      };

    perInstance =
      { roles, ... }:
      {
        nixosModule =
          { lib, ... }:
          {

            networking.nameservers = map (m: "127.0.0.1:5353#${roles.server.machines.${m}.settings.tld}") (
              lib.attrNames roles.server.machines
            );

            services.resolved.domains = map (m: "~${roles.server.machines.${m}.settings.tld}") (
              lib.attrNames roles.server.machines
            );

            services.unbound = {
              enable = true;
              settings = {
                server = {
                  port = 5353;
                  verbosity = 2;
                  interface = [ "127.0.0.1" ];
                  access-control = [ "127.0.0.0/8 allow" ];
                  do-not-query-localhost = "no";
                  domain-insecure = map (m: "${roles.server.machines.${m}.settings.tld}.") (
                    lib.attrNames roles.server.machines
                  );
                };

                # Default: forward everything else to DHCP-provided resolvers
                forward-zone = [
                  {
                    name = ".";
                    forward-addr = "127.0.0.53@53"; # Forward to systemd-resolved
                  }
                ];
                stub-zone = map (m: {
                  name = "${roles.server.machines.${m}.settings.tld}.";
                  stub-addr = "${roles.server.machines.${m}.settings.ip}";
                }) (lib.attrNames roles.server.machines);
              };
            };
          };
      };
  };
}
