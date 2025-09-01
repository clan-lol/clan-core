#!/usr/bin/env bash

set -eou pipefail

rsync --exclude result --exclude .direnv --exclude node_modules --delete -r ~/Projects/clan-core/pkgs/clan-app  mac-mini-dev:~/clan-core/pkgs

ssh mac-mini-dev "cd \$HOME/clan-core/pkgs/clan-app && nix build .#clan-app -Lv --show-trace"
ssh mac-mini-dev "cd \$HOME/clan-core/pkgs/clan-app && ./install-desktop.sh"

