#!/usr/bin/env bash

set -eux -o pipefail

script_dir=$(dirname "$(readlink -f "$0")")
cd "$script_dir/.."

trap 'rm -rf "$tmpdir"' EXIT
tmpdir=$(mktemp -d)

python "../clan-cli/api.py" > "$tmpdir/API.json"
json2ts --input "$tmpdir/API.json" > "$tmpdir/API.ts"

# compare sha256 sums of old and new API.ts
old_api_hash=$(sha256sum "./ui/api/API.ts" | cut -d ' ' -f 1)
new_api_hash=$(sha256sum "$tmpdir/API.ts" | cut -d ' ' -f 1)
if [ "$old_api_hash" != "$new_api_hash" ]; then
  cp "$tmpdir/API.json" "./ui/api/API.json"
  cp "$tmpdir/API.ts" "./ui/api/API.ts"
fi
