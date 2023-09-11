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
    system.clan.generateSecrets = pkgs.writeScript "generate-secrets" ''
      #!/bin/sh
      set -efu
      set -x # remove for prod

      PATH=$PATH:${lib.makeBinPath [
        config.clanCore.clanPkgs.clan-cli
      ]}

      # initialize secret store
      if ! clan secrets machines list | grep -q ${config.clanCore.machineName}; then (
        INITTMP=$(mktemp -d)
        trap 'rm -rf "$INITTMP"' EXIT
        ${pkgs.age}/bin/age-keygen -o "$INITTMP/secret" 2> "$INITTMP/public"
        PUBKEY=$(cat "$INITTMP/public" | sed 's/.*: //')
        clan secrets machines add ${config.clanCore.machineName} "$PUBKEY"
        tail -1 "$INITTMP/secret" | clan secrets set --machine ${config.clanCore.machineName} ${config.clanCore.machineName}-age.key
      ) fi

      ${lib.foldlAttrs (acc: n: v: ''
        ${acc}
        # ${n}
        # if any of the secrets are missing, we regenerate all connected facts/secrets
        (if ! ${lib.concatMapStringsSep " && " (x: "clan secrets get ${config.clanCore.machineName}-${x.name} >/dev/null") (lib.attrValues v.secrets)}; then

          facts=$(mktemp -d)
          trap "rm -rf $facts" EXIT
          secrets=$(mktemp -d)
          trap "rm -rf $secrets" EXIT
          ${v.generator}

          ${lib.concatMapStrings (fact: ''
            mkdir -p "$(dirname ${fact.path})"
            cp "$facts"/${fact.name} ${fact.path}
          '') (lib.attrValues v.facts)}

          ${lib.concatMapStrings (secret: ''
            cat "$secrets"/${secret.name} | clan secrets set --machine ${config.clanCore.machineName} ${config.clanCore.machineName}-${secret.name}
          '') (lib.attrValues v.secrets)}
        fi)
      '') "" config.clanCore.secrets}
    '';
    system.clan.deploySecrets = pkgs.writeScript "deploy-secrets" ''
      echo deployment is not needed for sops secret store, since the secrets are part of the flake
    '';
    sops.secrets = builtins.mapAttrs
      (name: _: {
        sopsFile = config.clanCore.clanDir + "/sops/secrets/${name}/secret";
        format = "binary";
      })
      secrets;
    # To get proper error messages about missing secrets we need a dummy secret file that is always present
    sops.defaultSopsFile = lib.mkIf config.sops.validateSopsFiles (lib.mkDefault (builtins.toString (pkgs.writeText "dummy.yaml" "")));
  };
}
