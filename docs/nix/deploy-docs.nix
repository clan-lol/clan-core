{
  writeShellScriptBin,
  coreutils,
  openssh,
  rsync,
  git,
  lib,
}:

writeShellScriptBin "deploy-docs" ''
  set -eu -o pipefail
  export PATH="${
    lib.makeBinPath [
      coreutils
      openssh
      rsync
      git
    ]
  }"

  cd "$(git rev-parse --show-toplevel)"

  #########################################
  #                                       #
  # DO NOT PRINT THE SSH KEY TO THE LOGS  #
  #                                       #
  #########################################
  tmpdir=$(mktemp -d)
  trap "rm -rf $tmpdir" EXIT

  if [ -n "''${SSH_HOMEPAGE_KEY-}" ]; then
    ( umask 0177 && echo "$SSH_HOMEPAGE_KEY" > "$tmpdir/ssh_key" )
    sshExtraArgs="-i $tmpdir/ssh_key"
  else
    sshExtraArgs=
  fi
  ###########################
  #                         #
  #    END OF DANGER ZONE   #
  #                         #
  ###########################

  git worktree add "$tmpdir/doc-pages" doc-pages

  set -x
  rsync \
    --checksum \
    --delete \
    -e "ssh -o StrictHostKeyChecking=no $sshExtraArgs" \
    -a "$tmpdir/doc-pages/" \
    www@clan.lol:/var/www/docs.clan.lol
  set +x

  git worktree remove "$tmpdir/doc-pages" 2>/dev/null || true

  if [ -e ./ssh_key ]; then
    rm ./ssh_key
  fi
''
