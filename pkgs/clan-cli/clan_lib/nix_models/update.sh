#!/usr/bin/env bash

set -euo pipefail

clanSchema=$(nix build .#schemas.clan-schema-abstract --print-out-paths)/schema.json
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"
nix run .#classgen -- "$clanSchema" "./clan.py"
