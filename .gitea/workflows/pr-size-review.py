"""Check that large PRs (>500 lines added) have at least 2 approving reviews."""

import json
import os
import sys
import urllib.request

MAX_ADDITIONS_SINGLE_REVIEW = 500
MIN_APPROVALS_LARGE_PR = 1


def api_get(url: str, token: str) -> object:
    if not url.startswith(("https://", "http://")):
        msg = f"URL must use http(s) scheme, got: {url}"
        raise ValueError(msg)
    req = urllib.request.Request(url, headers={"Authorization": f"token {token}"})  # noqa: S310
    with urllib.request.urlopen(req) as resp:  # noqa: S310
        return json.loads(resp.read())


def main() -> None:
    token = os.environ["GITEA_TOKEN"]
    pr_number = os.environ["PR_NUMBER"]
    repo = os.environ["REPO"]
    server_url = os.environ["SERVER_URL"]
    api_url = f"{server_url}/api/v1"

    # Get PR data
    pr_data = api_get(f"{api_url}/repos/{repo}/pulls/{pr_number}", token)
    if not isinstance(pr_data, dict):
        print("Error: unexpected API response for PR data", file=sys.stderr)
        sys.exit(1)
    additions: int = pr_data["additions"]
    pr_author: str = pr_data["user"]["login"]

    print(f"PR #{pr_number}: +{additions} lines added")

    if additions <= MAX_ADDITIONS_SINGLE_REVIEW:
        print(
            f"✅ PR has {additions} lines added (≤{MAX_ADDITIONS_SINGLE_REVIEW}). "
            "Single review sufficient."
        )
        sys.exit(0)

    print(
        f"⚠️  PR has {additions} lines added (>{MAX_ADDITIONS_SINGLE_REVIEW}). "
        f"Requires {MIN_APPROVALS_LARGE_PR} approving reviews."
    )

    # Get reviews
    reviews = api_get(f"{api_url}/repos/{repo}/pulls/{pr_number}/reviews", token)
    if not isinstance(reviews, list):
        print("Error: unexpected API response for reviews", file=sys.stderr)
        sys.exit(1)

    # Keep only the latest review per user, excluding the PR author
    latest_by_user: dict[str, str] = {}
    for review in sorted(reviews, key=lambda r: r["id"]):
        user = review["user"]["login"]
        if user != pr_author:
            latest_by_user[user] = review["state"]

    approvals = sum(1 for state in latest_by_user.values() if state == "APPROVED")
    print(f"Current unique approvals: {approvals}")

    if approvals >= MIN_APPROVALS_LARGE_PR:
        print(
            f"✅ PR has {approvals} approvals (≥{MIN_APPROVALS_LARGE_PR}). "
            "Requirement met."
        )
        sys.exit(0)
    else:
        print(
            f"❌ PR has {additions} lines added but only "
            f"{approvals}/{MIN_APPROVALS_LARGE_PR} required approvals.\n"
            "\n"
            f"PRs with more than {MAX_ADDITIONS_SINGLE_REVIEW} lines added "
            f"require {MIN_APPROVALS_LARGE_PR} approving reviews."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
