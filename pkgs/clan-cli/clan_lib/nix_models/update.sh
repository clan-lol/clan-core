#!/usr/bin/env bash

set -euo pipefail

jsonSchema=$(nix build .#schemas.inventory-schema-abstract --print-out-paths)/schema.json
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"
nix run .#classgen -- "$jsonSchema" "./inventory.py"
