{ config, lib, pkgs, ... }:
let
  secretsDir = config.clanCore.clanDir + "/sops/secrets";
  groupsDir = config.clanCore.clanDir + "/sops/groups";


  # My symlink is in the nixos module detected as a directory also it works in the repl. Is this because of pure evaluation?
  containsSymlink = path:
    builtins.pathExists path && (builtins.readFileType path == "directory" || builtins.readFileType path == "symlink");

  containsMachine = parent: name: type:
    type == "directory" && containsSymlink "${parent}/${name}/machines/${config.clanCore.machineName}";

  containsMachineOrGroups = name: type:
    (containsMachine secretsDir name type) || lib.any (group: type == "directory" && containsSymlink "${secretsDir}/${name}/groups/${group}") groups;

  filterDir = filter: dir:
    lib.optionalAttrs (builtins.pathExists dir)
      (lib.filterAttrs filter (builtins.readDir dir));

  groups = builtins.attrNames (filterDir (containsMachine groupsDir) groupsDir);
  secrets = filterDir containsMachineOrGroups secretsDir;
in
{
  config = lib.mkIf (config.clanCore.secretStore == "sops") {
    clanCore.secretsDirectory = "/run/secrets";
    clanCore.secretsPrefix = config.clanCore.machineName + "-";
    system.clan = {

      generateSecrets = pkgs.writeScript "generate-secrets" ''
        #!${pkgs.python3}/bin/python
        import json
        from clan_cli.secrets.sops_generate import generate_secrets_from_nix
        args = json.loads(${builtins.toJSON (builtins.toJSON { machine_name = config.clanCore.machineName; secret_submodules = config.clanCore.secrets; })})
        generate_secrets_from_nix(**args)
      '';
      uploadSecrets = pkgs.writeScript "upload-secrets" ''
        #!${pkgs.python3}/bin/python
        import json
        from clan_cli.secrets.sops_generate import upload_age_key_from_nix
        # the second toJSON is needed to escape the string for the python
        args = json.loads(${builtins.toJSON (builtins.toJSON { machine_name = config.clanCore.machineName; })})
        upload_age_key_from_nix(**args)
      '';
    };
    sops.secrets = builtins.mapAttrs
      (name: _: {
        sopsFile = config.clanCore.clanDir + "/sops/secrets/${name}/secret";
        format = "binary";
      })
      secrets;
    # To get proper error messages about missing secrets we need a dummy secret file that is always present
    sops.defaultSopsFile = lib.mkIf config.sops.validateSopsFiles (lib.mkDefault (builtins.toString (pkgs.writeText "dummy.yaml" "")));

    sops.age.keyFile = lib.mkIf (builtins.pathExists (config.clanCore.clanDir + "/sops/secrets/${config.clanCore.machineName}-age.key/secret"))
      (lib.mkDefault "/var/lib/sops-nix/key.txt");
    clanCore.secretsUploadDirectory = lib.mkDefault "/var/lib/sops-nix";
  };
}
