#!/usr/bin/env bash

set -eou pipefail

rsync --exclude result --exclude .direnv --exclude node_modules --delete -r ~/Projects/clan-core  mac-mini-dev:~/

ssh mac-mini-dev "cd \$HOME/clan-core/pkgs/clan-app && nix build .#clan-app -Lv --show-trace"
ssh mac-mini-dev "cd \$HOME/clan-core/pkgs/clan-app && ./install-desktop.sh"

