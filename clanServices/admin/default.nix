{
  _class = "clan.service";
  manifest.name = "clan-core/admin";
  manifest.description = "Adds a root user with ssh access";
  manifest.categories = [ "Utility" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.default = {
    description = "Placeholder role to apply the admin service";
    perInstance =
      { settings, ... }:
      {
        nixosModule =
          { lib, ... }:
          {
            warnings = lib.mkIf settings.deprecationWarning [
              "The clanServices/admin module is deprecated. See the migration guide: https://clan.lol/docs/unstable/guides/migrations/migrate-admin-service"
            ];
          };
      };
    interface =
      { lib, ... }:
      {
        options = {
          allowedKeys = lib.mkOption {
            default = { };
            type = lib.types.attrsOf lib.types.str;
            description = "The allowed public keys for ssh access to the admin user";
            example = {
              "key_1" = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD...";
            };
          };

          rsaHostKey.enable = lib.mkEnableOption "Generate RSA host key";

          # TODO: allow per-server domains that we than collect in the inventory
          #certicficateDomains = lib.mkOption {
          #  type = lib.types.listOf lib.types.str;
          #  default = [ ];
          #  example = [ "git.mydomain.com" ];
          #  description = "List of domains to include in the certificate. This option will not prepend the machine name in front of each domain.";
          #};

          certificateSearchDomains = lib.mkOption {
            type = lib.types.listOf lib.types.str;
            default = [ ];
            example = [ "mydomain.com" ];
            description = ''
              List of domains to include in the certificate.
              This option will prepend the machine name in front of each domain before adding it to the certificate.
            '';
          };

          deprecationWarning = lib.mkOption {
            type = lib.types.bool;
            default = true;
            example = false;
            internal = true;
          };
        };
      };
  };

  # We don't have a good way to specify dependencies between
  # clanServices for now. When it get's implemtende, we should just
  # use the ssh and users modules here.
  imports = [
    ./ssh.nix
    ./root-password.nix
  ];
}
