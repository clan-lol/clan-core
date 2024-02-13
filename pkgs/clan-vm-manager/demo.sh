#!/usr/bin/env bash

set -eux -o pipefail

rm -r ~/.config/clan

if [ -z "$1" ]; then
  echo "Usage: $0 <democlan>"
  exit 1
fi

democlan="$1"

clan history add "clan://$democlan#syncthing-peer1"
clan history add "clan://$democlan#syncthing-peer2"

clan history add "clan://$democlan#moonlight-peer1"
clan history add "clan://$democlan#moonlight-peer2"

clear
cat << EOF
Open up this link in a browser:
"clan://$democlan#syncthing-introducer"
EOF

cat << EOF
Execute this command to show waypipe windows:
$ clan --flake $democlan vms run --wayland wayland
EOF
