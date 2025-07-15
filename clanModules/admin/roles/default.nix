{ lib, config, ... }:
{

  options.clan.admin = {
    allowedKeys = lib.mkOption {
      default = { };
      type = lib.types.attrsOf lib.types.str;
      description = "The allowed public keys for ssh access to the admin user";
      example = {
        "key_1" = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD...";
      };
    };
  };
  # Bad practice.
  # Should we add 'clanModules' to specialArgs?
  imports = [
    ../../sshd
    ../../root-password
  ];
  config = {

    warnings = [
      "The clan.admin module is deprecated and will be removed on 2025-07-15.
      Please migrate to user-maintained configuration or the new equivalent clan services
      (https://docs.clan.lol/reference/clanServices)."
    ];

    users.users.root.openssh.authorizedKeys.keys = builtins.attrValues config.clan.admin.allowedKeys;
  };
}
