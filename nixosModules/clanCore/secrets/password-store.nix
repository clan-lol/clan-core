{ config, lib, pkgs, ... }:
let
  passwordstoreDir = "\${PASSWORD_STORE_DIR:-$HOME/.password-store}";
in
{
  options.clan.password-store.targetDirectory = lib.mkOption {
    type = lib.types.path;
    default = "/etc/secrets";
    description = ''
      The directory where the password store is uploaded to.
    '';
  };
  config = lib.mkIf (config.clanCore.secretStore == "password-store") {
    clanCore.secretsDirectory = config.clan.password-store.targetDirectory;
    clanCore.secretsUploadDirectory = config.clan.password-store.targetDirectory;
    system.clan.generateSecrets = lib.mkIf (config.clanCore.secrets != { }) (
      pkgs.writeScript "generate-secrets" ''
        #!/bin/sh
        set -efu

        test -d "$CLAN_DIR"
        PATH=${lib.makeBinPath [
          pkgs.pass
        ]}:$PATH

        # TODO maybe initialize password store if it doesn't exist yet

        ${lib.foldlAttrs (acc: n: v: ''
          ${acc}
          # ${n}
          # if any of the secrets are missing, we regenerate all connected facts/secrets
          (if ! (${lib.concatMapStringsSep " && " (x: "test -e ${passwordstoreDir}/machines/${config.clanCore.machineName}/${x.name}.gpg >/dev/null") (lib.attrValues v.secrets)}); then

            tmpdir=$(mktemp -d)
            trap "rm -rf $tmpdir" EXIT
            cd $tmpdir

            facts=$(mktemp -d)
            trap "rm -rf $facts" EXIT
            secrets=$(mktemp -d)
            trap "rm -rf $secrets" EXIT
            ( ${v.generator.finalScript} )

            ${lib.concatMapStrings (fact: ''
              mkdir -p "$CLAN_DIR"/"$(dirname ${fact.path})"
              cp "$facts"/${fact.name} "$CLAN_DIR"/${fact.path}
            '') (lib.attrValues v.facts)}

            ${lib.concatMapStrings (secret: ''
              cat "$secrets"/${secret.name} | pass insert -m machines/${config.clanCore.machineName}/${secret.name}
            '') (lib.attrValues v.secrets)}
          fi)
        '') "" config.clanCore.secrets}
      ''
    );
    system.clan.uploadSecrets = pkgs.writeScript "upload-secrets" ''
      #!/bin/sh
      set -efu

      umask 0077

      PATH=${lib.makeBinPath [
        pkgs.pass
        pkgs.git
        pkgs.findutils
        pkgs.rsync
      ]}:$PATH:${lib.getBin pkgs.openssh}

      if test -e ${passwordstoreDir}/.git; then
        local_pass_info=$(
          git -C ${passwordstoreDir} log -1 --format=%H machines/${config.clanCore.machineName}
          # we append a hash for every symlink, otherwise we would miss updates on
          # files where the symlink points to
          find ${passwordstoreDir}/machines/${config.clanCore.machineName} -type l \
              -exec realpath {} + |
            sort |
            xargs -r -n 1 git -C ${passwordstoreDir} log -1 --format=%H
        )
        remote_pass_info=$(ssh ${config.clan.networking.deploymentAddress} -- ${lib.escapeShellArg ''
          cat ${config.clan.password-store.targetDirectory}/.pass_info || :
        ''} || :)

        if test "$local_pass_info" = "$remote_pass_info"; then
          echo secrets already match
          exit 23
        fi
      fi

      find ${passwordstoreDir}/machines/${config.clanCore.machineName} -type f -follow ! -name .gpg-id |
      while read -r gpg_path; do

        rel_name=''${gpg_path#${passwordstoreDir}}
        rel_name=''${rel_name%.gpg}

        pass_date=$(
          if test -e ${passwordstoreDir}/.git; then
            git -C ${passwordstoreDir} log -1 --format=%aI "$gpg_path"
          fi
        )
        pass_name=$rel_name
        tmp_path="$SECRETS_DIR"/$(basename $rel_name)

        mkdir -p "$(dirname "$tmp_path")"
        pass show "$pass_name" > "$tmp_path"
        if [ -n "$pass_date" ]; then
          touch -d "$pass_date" "$tmp_path"
        fi
      done

      if test -n "''${local_pass_info-}"; then
        echo "$local_pass_info" > "$SECRETS_DIR"/.pass_info
      fi
    '';
  };
}

