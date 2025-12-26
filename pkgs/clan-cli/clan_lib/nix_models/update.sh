#!/usr/bin/env bash

set -euo pipefail

dir=$(nix build .#clan-types --print-out-paths)
cp "$dir/typing.py" typing.py
