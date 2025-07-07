#!/usr/bin/env bash
# Shared script for creating pull requests in Gitea workflows
set -euo pipefail

# Required environment variables:
# - CI_BOT_TOKEN: Gitea bot token for authentication
# - PR_BRANCH: Branch name for the pull request
# - PR_TITLE: Title of the pull request
# - PR_BODY: Body/description of the pull request

if [[ -z "${CI_BOT_TOKEN:-}" ]]; then
  echo "Error: CI_BOT_TOKEN is not set" >&2
  exit 1
fi

if [[ -z "${PR_BRANCH:-}" ]]; then
  echo "Error: PR_BRANCH is not set" >&2
  exit 1
fi

if [[ -z "${PR_TITLE:-}" ]]; then
  echo "Error: PR_TITLE is not set" >&2
  exit 1
fi

if [[ -z "${PR_BODY:-}" ]]; then
  echo "Error: PR_BODY is not set" >&2
  exit 1
fi

# Push the branch
git push origin "+HEAD:${PR_BRANCH}"

# Create pull request
resp=$(nix run --inputs-from . nixpkgs#curl -- -X POST \
  -H "Authorization: token $CI_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"head\": \"${PR_BRANCH}\",
    \"base\": \"main\",
    \"title\": \"${PR_TITLE}\",
    \"body\": \"${PR_BODY}\"
  }" \
  "https://git.clan.lol/api/v1/repos/clan/clan-core/pulls")

pr_number=$(echo "$resp" | jq -r '.number')

if [[ "$pr_number" == "null" ]]; then
  echo "Error creating pull request:" >&2
  echo "$resp" | jq . >&2
  exit 1
fi

echo "Created pull request #$pr_number"

# Merge when checks succeed
while true; do
  resp=$(nix run --inputs-from . nixpkgs#curl -- -X POST \
    -H "Authorization: token $CI_BOT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "Do": "merge",
      "merge_when_checks_succeed": true,
      "delete_branch_after_merge": true
    }' \
    "https://git.clan.lol/api/v1/repos/clan/clan-core/pulls/$pr_number/merge")
  msg=$(echo "$resp" | jq -r '.message')
  if [[ "$msg" != "Please try again later" ]]; then
    break
  fi
  echo "Retrying in 2 seconds..."
  sleep 2
done

echo "Pull request #$pr_number merge initiated"