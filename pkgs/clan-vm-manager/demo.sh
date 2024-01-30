#!/usr/bin/env bash

rm -r ~/.config/clan

clan history add "clan://~/Projects/democlan#syncthing-peer1"
clan history add "clan://~/Projects/democlan#syncthing-peer2"

clan history add "clan://~/Projects/democlan#moonlight-peer1"
clan history add "clan://~/Projects/democlan#moonlight-peer2"

clear
cat << EOF
Open up this link in a browser:
"clan://~/Projects/democlan#syncthing-introducer"
EOF


cat << EOF
Execute this command to show waypipe windows:
$ clan --flake ~/Projects/democlan/ vms run --wayland wayland
EOF
