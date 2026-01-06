#!/usr/bin/env bash

set -euo pipefail

dir=$(nix build .#clan-types --no-link --print-out-paths)
cp -f "$dir/typing.py" "$(dirname "$0")/typing.py"
