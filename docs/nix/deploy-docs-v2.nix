{
  writeShellScriptBin,
  coreutils,
  openssh,
  rsync,
  git,
  nix,
  lib,
  docs,
}:

writeShellScriptBin "deploy-docs-v2" ''
  set -eu -o pipefail
  export PATH="${
    lib.makeBinPath [
      coreutils
      openssh
      rsync
      git
      nix
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

  VERSION_NAME=${builtins.readFile ../../VERSION}

  echo "Deploying docs for version: $VERSION_NAME"

  set -x
  rsync \
    --checksum \
    --delete \
    -e "ssh -o StrictHostKeyChecking=no $sshExtraArgs" \
    -a "${docs}/" \
    --mkpath \
    "www@clan.lol:/var/www/versioned-docs/$VERSION_NAME"
  set +x
''
