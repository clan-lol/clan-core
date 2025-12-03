{
  roles.default.perInstance =
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
          stringSet = list: builtins.attrNames (builtins.groupBy lib.id list);

          domains = stringSet settings.certificateSearchDomains;

        in
        {

          users.users.root.openssh.authorizedKeys.keys = builtins.attrValues settings.allowedKeys;

          services.openssh = {
            enable = true;
            settings.PasswordAuthentication = false;

            settings.HostCertificate = lib.mkIf (
              settings.certificateSearchDomains != [ ]
            ) config.clan.core.vars.generators.openssh-cert.files."ssh.id_ed25519-cert.pub".path;

            hostKeys = [
              {
                path = config.clan.core.vars.generators.openssh.files."ssh.id_ed25519".path;
                type = "ed25519";
              }
            ]
            ++ lib.optional settings.rsaHostKey.enable {
              path = config.clan.core.vars.generators.openssh-rsa.files."ssh.id_rsa".path;
              type = "rsa";
            };
          };

          clan.core.vars.generators.openssh = {
            files."ssh.id_ed25519" = { };
            files."ssh.id_ed25519.pub".secret = false;
            runtimeInputs = [
              pkgs.coreutils
              pkgs.openssh
            ];
            script = ''
              ssh-keygen -t ed25519 -N "" -C "" -f "$out"/ssh.id_ed25519
            '';
          };

          programs.ssh.knownHosts.clan-sshd-self-ed25519 = {
            hostNames = [
              "localhost"
              config.networking.hostName
            ]
            ++ (lib.optional (config.networking.domain != null) config.networking.fqdn);
            publicKey = config.clan.core.vars.generators.openssh.files."ssh.id_ed25519.pub".value;
          };

          clan.core.vars.generators.openssh-rsa = lib.mkIf settings.rsaHostKey.enable {
            files."ssh.id_rsa" = { };
            files."ssh.id_rsa.pub".secret = false;
            runtimeInputs = [
              pkgs.coreutils
              pkgs.openssh
            ];
            script = ''
              ssh-keygen -t rsa -b 4096 -N "" -C "" -f "$out"/ssh.id_rsa
            '';
          };

          clan.core.vars.generators.openssh-cert = lib.mkIf (settings.certificateSearchDomains != [ ]) {
            files."ssh.id_ed25519-cert.pub".secret = false;
            dependencies = [
              "openssh"
              "openssh-ca"
            ];
            validation = {
              name = config.clan.core.settings.machine.name;
              domains = lib.genAttrs settings.certificateSearchDomains lib.id;
            };
            runtimeInputs = [
              pkgs.openssh
              pkgs.jq
            ];
            script = ''
              ssh-keygen \
                -s $in/openssh-ca/id_ed25519 \
                -I ${config.clan.core.settings.machine.name} \
                -h \
                -n ${lib.concatMapStringsSep "," (d: "${config.clan.core.settings.machine.name}.${d}") domains} \
                $in/openssh/ssh.id_ed25519.pub
              mv $in/openssh/ssh.id_ed25519-cert.pub "$out"/ssh.id_ed25519-cert.pub
            '';
          };

          clan.core.vars.generators.openssh-ca = lib.mkIf (settings.certificateSearchDomains != [ ]) {
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
              ssh-keygen -t ed25519 -N "" -C "" -f "$out"/id_ed25519
            '';
          };

          programs.ssh.knownHosts.ssh-ca = lib.mkIf (settings.certificateSearchDomains != [ ]) {
            certAuthority = true;
            extraHostNames = builtins.map (domain: "*.${domain}") settings.certificateSearchDomains;
            publicKey = config.clan.core.vars.generators.openssh-ca.files."id_ed25519.pub".value;
          };
        };
    };
}
