#!/usr/bin/env bash

set -euo pipefail

dir=$(nix build .#clan-types --no-link --print-out-paths)
SCRIPT_DIR=$(dirname "$0")

cd "$SCRIPT_DIR"
cp -f "$dir/typing.py" "typing.py"
