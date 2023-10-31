#!/usr/bin/env bash
set -euo pipefail

remoteName="${1:-origin}"
targetBranch="${2:-main}"
shift && shift
TMPDIR="$(mktemp -d)"
currentBranch="$(git rev-parse --abbrev-ref HEAD)"
user="$(tea login list -o simple | cut -d" " -f4 | head -n1)"
tempRemoteBranch="$user-$currentBranch"

nix fmt -- --fail-on-change

git log --reverse --pretty="format:%s%n%n%b%n%n" "$remoteName/$targetBranch..HEAD" > "$TMPDIR"/commit-msg

$EDITOR "$TMPDIR"/commit-msg

COMMIT_MSG=$(cat "$TMPDIR"/commit-msg)

firstLine=$(echo "$COMMIT_MSG" | head -n1)
rest=$(echo "$COMMIT_MSG" | tail -n+2)

if [[ "$firstLine" == "$rest" ]]; then
  rest=""
fi
git push --force -u "$remoteName" HEAD:refs/heads/"$tempRemoteBranch"

tea pr create \
  --title "$firstLine" \
  --description "$rest" \
  --head "$tempRemoteBranch" \
  --base "$targetBranch" \
  "$@"
