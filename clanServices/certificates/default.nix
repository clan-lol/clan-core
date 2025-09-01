{ ... }:
{
  _class = "clan.service";
  manifest.name = "certificates";
  manifest.description = "Sets up a certificates internal to your Clan";
  manifest.categories = [ "Network" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.ca = {

    interface =
      { lib, ... }:
      {

        options.acmeEmail = lib.mkOption {
          type = lib.types.str;
          default = "none@none.tld";
          description = ''
            Email address for account creation and correspondence from the CA.
            It is recommended to use the same email for all certs to avoid account
            creation limits.
          '';
        };

        options.tlds = lib.mkOption {
          type = lib.types.listOf lib.types.str;
          description = "Top level domain for this CA. Certificates will be issued and trusted for *.<tld>";
        };

        options.expire = lib.mkOption {
          type = lib.types.nullOr lib.types.str;
          description = "When the certificate should expire. Defaults to no expiry";
          default = null;
          example = "8760h";
        };
      };

    perInstance =
      { settings, ... }:
      {
        nixosModule =
          {
            config,
            pkgs,
            lib,
            ...
          }:
          let
            domains = map (tld: "ca.${tld}") settings.tlds;
          in
          {
            security.acme.defaults.email = settings.acmeEmail;
            security.acme = {
              certs = builtins.listToAttrs (
                map (domain: {
                  name = domain;
                  value = {
                    server = "https://${domain}:1443/acme/acme/directory";
                  };
                }) domains
              );
            };

            networking.firewall.allowedTCPPorts = [
              80
              443
            ];

            services.nginx = {
              enable = true;
              recommendedProxySettings = true;
              virtualHosts = builtins.listToAttrs (
                map (domain: {
                  name = domain;
                  value = {
                    addSSL = true;
                    enableACME = true;
                    locations."/".proxyPass = "https://localhost:1443";
                    locations."= /ca.crt".alias =
                      config.clan.core.vars.generators.step-intermediate-cert.files."intermediate.crt".path;
                  };
                }) domains
              );
            };

            clan.core.vars.generators = {

              # Intermediate key generator
              "step-intermediate-key" = {
                files."intermediate.key" = {
                  secret = true;
                  deploy = true;
                  owner = "step-ca";
                  group = "step-ca";
                };
                runtimeInputs = [ pkgs.step-cli ];
                script = ''
                  step crypto keypair --kty EC --curve P-256 --no-password --insecure $out/intermediate.pub $out/intermediate.key
                '';
              };

              # Intermediate certificate generator
              "step-intermediate-cert" = {
                files."intermediate.crt".secret = false;
                dependencies = [
                  "step-ca"
                  "step-intermediate-key"
                ];
                runtimeInputs = [ pkgs.step-cli ];
                script = ''
                  # Create intermediate certificate
                  step certificate create \
                    --ca $in/step-ca/ca.crt \
                    --ca-key $in/step-ca/ca.key \
                    --ca-password-file /dev/null \
                    --key $in/step-intermediate-key/intermediate.key \
                    --template ${pkgs.writeText "intermediate.tmpl" ''
                      {
                        "subject": {{ toJson .Subject }},
                        "keyUsage": ["certSign", "crlSign"],
                        "basicConstraints": {
                          "isCA": true,
                          "maxPathLen": 0
                        },
                        "nameConstraints": {
                          "critical": true,
                          "permittedDNSDomains": [${
                            (lib.strings.concatStringsSep "," (map (tld: ''"${tld}"'') settings.tlds))
                          }]
                        }
                      }
                    ''} ${lib.optionalString (settings.expire != null) "--not-after ${settings.expire}"} \
                    --no-password --insecure \
                    "Clan Intermediate CA" \
                    $out/intermediate.crt
                '';
              };
            };

            services.step-ca = {
              enable = true;
              intermediatePasswordFile = "/dev/null";
              address = "0.0.0.0";
              port = 1443;
              settings = {
                root = config.clan.core.vars.generators.step-ca.files."ca.crt".path;
                crt = config.clan.core.vars.generators.step-intermediate-cert.files."intermediate.crt".path;
                key = config.clan.core.vars.generators.step-intermediate-key.files."intermediate.key".path;
                dnsNames = domains;
                logger.format = "text";
                db = {
                  type = "badger";
                  dataSource = "/var/lib/step-ca/db";
                };
                authority = {
                  provisioners = [
                    {
                      type = "ACME";
                      name = "acme";
                      forceCN = true;
                    }
                  ];
                  claims = {
                    maxTLSCertDuration = "2160h";
                    defaultTLSCertDuration = "2160h";
                  };
                  backdate = "1m0s";
                };
                tls = {
                  cipherSuites = [
                    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256"
                    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256"
                  ];
                  minVersion = 1.2;
                  maxVersion = 1.3;
                  renegotiation = false;
                };
              };
            };
          };
      };
  };

  # Empty role, so we can add non-ca machins to the instance to trust the CA
  roles.default = {
    interface =
      { lib, ... }:
      {
        options.acmeEmail = lib.mkOption {
          type = lib.types.str;
          default = "none@none.tld";
          description = ''
            Email address for account creation and correspondence from the CA.
            It is recommended to use the same email for all certs to avoid account
            creation limits.
          '';
        };
      };

    perInstance =
      { settings, ... }:
      {
        nixosModule.security.acme.defaults.email = settings.acmeEmail;
      };
  };

  # All machines (independent of role) will trust the CA
  perMachine.nixosModule =
    { pkgs, config, ... }:
    {
      # Root CA generator
      clan.core.vars.generators = {
        "step-ca" = {
          share = true;
          files."ca.key" = {
            secret = true;
            deploy = false;
          };
          files."ca.crt".secret = false;
          runtimeInputs = [ pkgs.step-cli ];
          script = ''
            step certificate create --template ${pkgs.writeText "root.tmpl" ''
              {
                "subject": {{ toJson .Subject }},
                "issuer": {{ toJson .Subject }},
                "keyUsage": ["certSign", "crlSign"],
                "basicConstraints": {
                  "isCA": true,
                  "maxPathLen": 1
                }
              }
            ''} "Clan Root CA" $out/ca.crt $out/ca.key \
              --kty EC --curve P-256 \
              --no-password --insecure
          '';
        };
      };
      security.pki.certificateFiles = [ config.clan.core.vars.generators."step-ca".files."ca.crt".path ];
      environment.systemPackages = [ pkgs.openssl ];
      security.acme.acceptTerms = true;
    };
}
