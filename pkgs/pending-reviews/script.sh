#!/usr/bin/env bash
set -euo pipefail

display_pr() { jq -r '.[] | "\(.url) | \(.title) from \(.user.login)"'; }

echo "# Review needed"
curl -s 'https://git.clan.lol/api/v1/repos/clan/clan-core/pulls?state=closed&sort=leastupdate&labels=8' | display_pr

echo "# Changes requested"
curl -s 'https://git.clan.lol/api/v1/repos/clan/clan-core/pulls?sort=leastupdate&labels=9' | display_pr
