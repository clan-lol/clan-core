#!/usr/bin/env bash

set -eux -o pipefail

script_dir=$(dirname "$(readlink -f "$0")")

clan_cli="$script_dir/../clan-cli"

trap 'rm -rf "$tmpdir"' EXIT
tmpdir=$(mktemp -d)

python "$clan_cli/api.py" > "$tmpdir/API.json"
json2ts --input "$tmpdir/API.json" > "$tmpdir/API.ts"

# compare sha256 sums of old and new API.ts
old_api_hash=$(sha256sum "$script_dir/../api/API.ts" | cut -d ' ' -f 1)
new_api_hash=$(sha256sum "$tmpdir/API.ts" | cut -d ' ' -f 1)
if [ "$old_api_hash" != "$new_api_hash" ]; then
  cp "$tmpdir/API.json" "$script_dir/../api/API.json"
  cp "$tmpdir/API.ts" "$script_dir/../api/API.ts"
fi
