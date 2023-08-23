{ lib, config, ... }:
let
  encryptedForThisMachine = name: type:
    let
      symlink = config.clan.sops.sopsDirectory + "/secrets/${name}/machines/${config.clan.sops.machineName}";
    in
    # WTF, nix bug, my symlink is in the nixos module detected as a directory also it works in the repl
    type == "directory" && (builtins.readFileType symlink == "directory" || builtins.readFileType symlink == "symlink");
  secrets = lib.filterAttrs encryptedForThisMachine (builtins.readDir (config.clan.sops.sopsDirectory + "/secrets"));
in
{
  imports = [
  ];
  options = {
    clan.sops = {
      machineName = lib.mkOption {
        type = lib.types.str;
        default = config.networking.hostName;
        description = ''
          Machine used to lookup secrets in the sops directory.
        '';
      };
      sopsDirectory = lib.mkOption {
        type = lib.types.path;
        description = ''
          Sops toplevel directory that stores users, machines, groups and secrets.
        '';
      };
    };
  };
  config = {
    sops.secrets = builtins.mapAttrs
      (name: _: {
        sopsFile = config.clan.sops.sopsDirectory + "/secrets/${name}/secret";
        format = "binary";
      })
      secrets;
  };
}
