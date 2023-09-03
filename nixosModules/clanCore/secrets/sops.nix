{ config, lib, pkgs, ... }:
{
  config = {
    system.clan.generateSecrets = pkgs.writeScript "generate_secrets" ''
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
    sops.secrets =
      let
        secretsDir = config.clanCore.clanDir + "/sops/secrets";
        encryptedForThisMachine = name: type:
          let
            symlink = secretsDir + "/${name}/machines/${config.clanCore.machineName}";
          in
          # WTF, nix bug, my symlink is in the nixos module detected as a directory also it works in the repl
          type == "directory" && (builtins.readFileType symlink == "directory" || builtins.readFileType symlink == "symlink");
        secrets =
          if !builtins.pathExists secretsDir
          then { }
          else lib.filterAttrs encryptedForThisMachine (builtins.readDir secretsDir);
      in
      builtins.mapAttrs
        (name: _: {
          sopsFile = config.clanCore.clanDir + "/sops/secrets/${name}/secret";
          format = "binary";
        })
        secrets;
    # To get proper error messages about missing secrets we need a dummy secret file that is always present
    sops.defaultSopsFile = lib.mkIf config.sops.validateSopsFiles (lib.mkDefault (builtins.toString (pkgs.writeText "dummy.yaml" "")));
  };
}
