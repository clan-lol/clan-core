{
  config,
  lib,
  pkgs,
  ...
}:
let
  secretsDir = config.clan.core.clanDir + "/sops/secrets";
  groupsDir = config.clan.core.clanDir + "/sops/groups";

  # My symlink is in the nixos module detected as a directory also it works in the repl. Is this because of pure evaluation?
  containsSymlink =
    path:
    builtins.pathExists path
    && (builtins.readFileType path == "directory" || builtins.readFileType path == "symlink");

  containsMachine =
    parent: name: type:
    type == "directory" && containsSymlink "${parent}/${name}/machines/${config.clan.core.machineName}";

  containsMachineOrGroups =
    name: type:
    (containsMachine secretsDir name type)
    || lib.any (
      group: type == "directory" && containsSymlink "${secretsDir}/${name}/groups/${group}"
    ) groups;

  filterDir =
    filter: dir:
    lib.optionalAttrs (builtins.pathExists dir) (lib.filterAttrs filter (builtins.readDir dir));

  groups = builtins.attrNames (filterDir (containsMachine groupsDir) groupsDir);
  secrets = filterDir containsMachineOrGroups secretsDir;
in
{
  config.clan.core.vars.settings = lib.mkIf (config.clan.core.vars.settings.secretStore == "sops") {
    # Before we generate a secret we cannot know the path yet, so we need to set it to an empty string
    fileModule = file: {
      path =
        lib.mkIf file.secret
          config.sops.secrets.${"${config.clan.core.machineName}-${file.config.name}"}.path
            or "/no-such-path";
    };
    secretModule = "clan_cli.vars.secret_modules.sops";
    secretUploadDirectory = lib.mkDefault "/var/lib/sops-nix";
  };

  config.sops = lib.mkIf (config.clan.core.vars.settings.secretStore == "sops") {
    secrets = builtins.mapAttrs (name: _: {
      sopsFile = config.clan.core.clanDir + "/sops/secrets/${name}/secret";
      format = "binary";
    }) secrets;
    # To get proper error messages about missing secrets we need a dummy secret file that is always present
    defaultSopsFile = lib.mkIf config.sops.validateSopsFiles (
      lib.mkDefault (builtins.toString (pkgs.writeText "dummy.yaml" ""))
    );
    age.keyFile = lib.mkIf (builtins.pathExists (
      config.clan.core.clanDir + "/sops/secrets/${config.clan.core.machineName}-age.key/secret"
    )) (lib.mkDefault "/var/lib/sops-nix/key.txt");
  };
}
