#!/usr/bin/env bash
set -euo pipefail

remoteName="${1:-origin}"
targetBranch="${2:-main}"
shift && shift
tea-create-pr "$remoteName" "$targetBranch" --assignees clan-bot "$@"
