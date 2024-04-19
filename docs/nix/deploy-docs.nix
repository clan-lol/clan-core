{
  writeShellScriptBin,
  coreutils,
  openssh,
  rsync,
  lib,
  docs,
}:

writeShellScriptBin "deploy-docs" ''
  set -eux -o pipefail
  export PATH="${
    lib.makeBinPath [
      coreutils
      openssh
      rsync
    ]
  }"

  if [ -n "''${SSH_HOMEPAGE_KEY:-}" ]; then
    echo "$SSH_HOMEPAGE_KEY" > ./ssh_key
    chmod 600 ./ssh_key
    sshExtraArgs="-i ./ssh_key"
  else
    sshExtraArgs=
  fi

  rsync \
    -e "ssh -o StrictHostKeyChecking=no $sshExtraArgs" \
    -a ${docs}/ \
    www@clan.lol:/var/www/docs.clan.lol

  if [ -e ./ssh_key ]; then
    rm ./ssh_key
  fi
''
