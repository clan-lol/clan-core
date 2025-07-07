{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/sshd";
  manifest.description = "Enables secure remote access to the machine over SSH";
  manifest.categories = [
    "System"
    "Network"
  ];

  roles.client = {
    interface =
      { lib, ... }:
      {
        options.certificate = {
          searchDomains = lib.mkOption {
            type = lib.types.listOf lib.types.str;
            default = [ ];
            example = [ "mydomain.com" ];
            description = ''
              List of domains to include in the certificate.
              This option will prepend the machine name in front of each domain
              before adding it to the certificate.
            '';
          };
        };
      };

    perInstance =
      { settings, ... }:
      {
        nixosModule =
          {
            config,
            lib,
            pkgs,
            ...
          }:
          {

            clan.core.vars.generators.openssh-ca = lib.mkIf (settings.certificate.searchDomains != [ ]) {
              share = true;
              files.id_ed25519.deploy = false;
              files."id_ed25519.pub" = {
                deploy = false;
                secret = false;
              };
              runtimeInputs = [
                pkgs.openssh
              ];
              script = ''
                ssh-keygen -t ed25519 -N "" -f "$out"/id_ed25519
              '';
            };

            programs.ssh.knownHosts.ssh-ca = lib.mkIf (settings.certificate.searchDomains != [ ]) {
              certAuthority = true;
              extraHostNames = builtins.map (domain: "*.${domain}") settings.certificate.searchDomains;
              publicKey = config.clan.core.vars.generators.openssh-ca.files."id_ed25519.pub".value;
            };
          };
      };
  };

  roles.server = {
    interface =
      { lib, ... }:
      {
        options = {
          hostKeys.rsa.enable = lib.mkEnableOption "Generate RSA host key";

          certificate = {
            searchDomains = lib.mkOption {
              type = lib.types.listOf lib.types.str;
              default = [ ];
              example = [ "mydomain.com" ];
              description = ''
                List of domains to include in the certificate. This option will
                prepend the machine name in front of each domain before adding
                it to the certificate.
              '';
            };
          };
        };
      };

    perInstance =
      { settings, ... }:
      {
        nixosModule =
          {
            config,
            lib,
            pkgs,
            ...
          }:
          {

            clan.core.vars.generators = {

              openssh-ca = lib.mkIf (settings.certificate.searchDomains != [ ]) {
                share = true;
                files.id_ed25519.deploy = false;
                files."id_ed25519.pub" = {
                  deploy = false;
                  secret = false;
                };
                runtimeInputs = [
                  pkgs.openssh
                ];
                script = ''
                  ssh-keygen -t ed25519 -N "" -f "$out"/id_ed25519
                '';
              };

              openssh-cert = lib.mkIf (settings.certificate.searchDomains != [ ]) {
                files."ssh.id_ed25519-cert.pub".secret = false;
                dependencies = [
                  "openssh"
                  "openssh-ca"
                ];
                validation = {
                  name = config.clan.core.settings.machine.name;
                  domains = lib.genAttrs settings.certificate.searchDomains lib.id;
                };
                runtimeInputs = [
                  pkgs.openssh
                  pkgs.jq
                ];
                script =
                  let
                    stringSet = list: builtins.attrNames (builtins.groupBy lib.id list);
                    domains = stringSet settings.certificate.searchDomains;
                  in
                  ''
                    ssh-keygen \
                      -s $in/openssh-ca/id_ed25519 \
                      -I ${config.clan.core.settings.machine.name} \
                      -h \
                      -n ${lib.concatMapStringsSep "," (d: "${config.clan.core.settings.machine.name}.${d}") domains} \
                      $in/openssh/ssh.id_ed25519.pub
                    mv $in/openssh/ssh.id_ed25519-cert.pub "$out"/ssh.id_ed25519-cert.pub
                  '';
              };

              openssh-rsa = lib.mkIf settings.hostKeys.rsa.enable {
                files."ssh.id_rsa" = { };
                files."ssh.id_rsa.pub".secret = false;
                runtimeInputs = [
                  pkgs.coreutils
                  pkgs.openssh
                ];
                script = ''
                  ssh-keygen -t rsa -b 4096 -N "" -f "$out"/ssh.id_rsa
                '';
              };

              openssh = {
                files."ssh.id_ed25519" = { };
                files."ssh.id_ed25519.pub".secret = false;
                migrateFact = "openssh";
                runtimeInputs = [
                  pkgs.coreutils
                  pkgs.openssh
                ];
                script = ''
                  ssh-keygen -t ed25519 -N "" -f "$out"/ssh.id_ed25519
                '';
              };
            };

            programs.ssh.knownHosts.ssh-ca = lib.mkIf (settings.certificate.searchDomains != [ ]) {
              certAuthority = true;
              extraHostNames = builtins.map (domain: "*.${domain}") settings.certificate.searchDomains;
              publicKey = config.clan.core.vars.generators.openssh-ca.files."id_ed25519.pub".value;
            };

            services.openssh = {
              enable = true;
              settings.PasswordAuthentication = false;

              settings.HostCertificate = lib.mkIf (
                settings.certificate.searchDomains != [ ]
              ) config.clan.core.vars.generators.openssh-cert.files."ssh.id_ed25519-cert.pub".path;

              hostKeys =
                [
                  {
                    path = config.clan.core.vars.generators.openssh.files."ssh.id_ed25519".path;
                    type = "ed25519";
                  }
                ]
                ++ lib.optional settings.hostKeys.rsa.enable {
                  path = config.clan.core.vars.generators.openssh-rsa.files."ssh.id_rsa".path;
                  type = "rsa";
                };
            };

            programs.ssh.knownHosts.clan-sshd-self-ed25519 = {
              hostNames = [
                "localhost"
                config.networking.hostName
              ] ++ (lib.optional (config.networking.domain != null) config.networking.fqdn);
              publicKey = config.clan.core.vars.generators.openssh.files."ssh.id_ed25519.pub".value;
            };
          };
      };
  };
}
