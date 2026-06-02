#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: clan-release-diff <old-branch> [new-branch]

Compare NixOS/clan options between two branches.

Arguments:
  old-branch    Base branch to compare from (e.g. 25.11)
  new-branch    Branch to compare to (default: current working tree)

Examples:
  clan-release-diff 25.11
  clan-release-diff 25.11 main
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage
    exit 0
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
    usage
    exit 2
fi

old_branch="$1"
new_branch="${2:-}"

# Flake ref for the old branch (always a git ref)
old_ref="git+file:.?ref=refs/heads/${old_branch}"

# Flake ref for the new branch (working tree if omitted, git ref otherwise)
if [[ -z "$new_branch" ]]; then
    new_ref="."
    new_label="(working tree)"
else
    new_ref="git+file:.?ref=refs/heads/${new_branch}"
    new_label="$new_branch"
fi

echo "Building options JSON for ${old_branch}..." >&2
old_clan=$(nix build "${old_ref}#legacyPackages.x86_64-linux.clan-options" --no-link --print-out-paths)
old_nixos=$(nix build "${old_ref}#legacyPackages.x86_64-linux.jsonDocs.clanCore" --no-link --print-out-paths)
old_services=$(nix build "${old_ref}#legacyPackages.x86_64-linux.clanModulesViaService" --no-link --print-out-paths)

echo "Building options JSON for ${new_label}..." >&2
new_clan=$(nix build "${new_ref}#legacyPackages.x86_64-linux.clan-options" --no-link --print-out-paths)
new_nixos=$(nix build "${new_ref}#legacyPackages.x86_64-linux.jsonDocs.clanCore" --no-link --print-out-paths)
new_services=$(nix build "${new_ref}#legacyPackages.x86_64-linux.clanModulesViaService" --no-link --print-out-paths)

json="share/doc/nixos/options.json"

exec @diff@ layers \
    --old-label "$old_branch" --new-label "$new_label" \
    --old-clan "$old_clan/$json" \
    --new-clan "$new_clan/$json" \
    --old-nixos "$old_nixos/$json" \
    --new-nixos "$new_nixos/$json" \
    --old-services "$old_services" \
    --new-services "$new_services"
