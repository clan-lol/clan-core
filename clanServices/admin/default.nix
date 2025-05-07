{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/admin";

  roles.default = {
    interface =
      { lib, ... }:
      {
        options.allowedKeys = lib.mkOption {
          default = { };
          type = lib.types.attrsOf lib.types.str;
          description = "The allowed public keys for ssh access to the admin user";
          example = {
            "key_1" = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD...";
          };
        };

      };

    perInstance =
      { settings, ... }:
      {
        nixosModule =
          { ... }:
          {

            imports = [
              ../../clanModules/sshd
              ../../clanModules/root-password
            ];

            users.users.root.openssh.authorizedKeys.keys = builtins.attrValues settings.allowedKeys;
          };
      };
  };
}
