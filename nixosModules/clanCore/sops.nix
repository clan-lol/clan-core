{ lib, config, ... }:
let
  secretsDir = config.clan.core.settings.directory + "/sops/secrets";
  groupsDir = config.clan.core.settings.directory + "/sops/groups";

  # My symlink is in the nixos module detected as a directory also it works in the repl. Is this because of pure evaluation?
  containsSymlink =
    path:
    builtins.pathExists path
    && (builtins.readFileType path == "directory" || builtins.readFileType path == "symlink");

  containsMachine =
    parent: name: type:
    type == "directory"
    && containsSymlink "${parent}/${name}/machines/${config.clan.core.settings.machine.name}";

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
  options = {
    clan.core.sops.defaultGroups = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      example = [ "admins" ];
      description = "The default groups to use for encryption when no groups are specified.";
    };
  };
  config = {
    sops.secrets = builtins.mapAttrs (name: _: {
      sopsFile = config.clan.core.settings.directory + "/sops/secrets/${name}/secret";
      format = "binary";
    }) secrets;
  };
}
