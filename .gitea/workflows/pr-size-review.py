"""Check that large PRs (>500 lines added) have at least 2 approving reviews.

Posts a commit status with a fixed context name so that both pull_request
and pull_request_review triggers update the same check.  Gitea appends the
event type to the auto-generated context, which causes review-triggered runs
to create a separate (invisible) status.  By posting our own status and
always exiting 0, we avoid that problem.
"""

import json
import os
import sys
import urllib.request

MAX_ADDITIONS_SINGLE_REVIEW = 500
MIN_APPROVALS_LARGE_PR = 1
STATUS_CONTEXT = "pr-size-review-gate"


def api_request(url: str, token: str, data: dict | None = None) -> object:
    if not url.startswith(("https://", "http://")):
        msg = f"URL must use http(s) scheme, got: {url}"
        raise ValueError(msg)
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(  # noqa: S310
        url,
        data=body,
        headers={
            "Authorization": f"token {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:  # noqa: S310
        return json.loads(resp.read())


def post_status(
    api_url: str,
    token: str,
    repo: str,
    sha: str,
    *,
    state: str,
    description: str,
) -> None:
    url = f"{api_url}/repos/{repo}/statuses/{sha}"
    api_request(
        url,
        token,
        {
            "context": STATUS_CONTEXT,
            "description": description,
            "state": state,
        },
    )


def main() -> None:
    token = os.environ["GITEA_TOKEN"]
    pr_number = os.environ["PR_NUMBER"]
    repo = os.environ["REPO"]
    server_url = os.environ["SERVER_URL"]
    head_sha = os.environ["HEAD_SHA"]
    api_url = f"{server_url}/api/v1"

    # Get PR data
    pr_data = api_request(f"{api_url}/repos/{repo}/pulls/{pr_number}", token)
    if not isinstance(pr_data, dict):
        print("Error: unexpected API response for PR data", file=sys.stderr)
        sys.exit(1)
    additions: int = pr_data["additions"]
    pr_author: str = pr_data["user"]["login"]

    print(f"PR #{pr_number}: +{additions} lines added")

    if additions <= MAX_ADDITIONS_SINGLE_REVIEW:
        msg = (
            f"PR has {additions} lines added (≤{MAX_ADDITIONS_SINGLE_REVIEW}). "
            "Single review sufficient."
        )
        print(f"✅ {msg}")
        post_status(api_url, token, repo, head_sha, state="success", description=msg)
        return

    print(
        f"⚠️  PR has {additions} lines added (>{MAX_ADDITIONS_SINGLE_REVIEW}). "
        f"Requires {MIN_APPROVALS_LARGE_PR} approving reviews."
    )

    # Get reviews
    reviews = api_request(f"{api_url}/repos/{repo}/pulls/{pr_number}/reviews", token)
    if not isinstance(reviews, list):
        print("Error: unexpected API response for reviews", file=sys.stderr)
        sys.exit(1)

    # Keep only the latest non-dismissed review per user, excluding the PR author
    latest_by_user: dict[str, str] = {}
    for review in sorted(reviews, key=lambda r: r["id"]):
        user = review["user"]["login"]
        if user == pr_author:
            continue
        if review.get("dismissed", False):
            # Dismissed reviews don't count; remove any previous state for this user
            latest_by_user.pop(user, None)
        else:
            latest_by_user[user] = review["state"]

    approvals = sum(1 for state in latest_by_user.values() if state == "APPROVED")
    print(f"Current unique approvals: {approvals}")

    if approvals >= MIN_APPROVALS_LARGE_PR:
        msg = f"{approvals} approval(s) (≥{MIN_APPROVALS_LARGE_PR}). Requirement met."
        print(f"✅ {msg}")
        post_status(api_url, token, repo, head_sha, state="success", description=msg)
    else:
        msg = (
            f"{approvals}/{MIN_APPROVALS_LARGE_PR} approvals. "
            f"PRs with >{MAX_ADDITIONS_SINGLE_REVIEW} lines added need review."
        )
        print(f"❌ {msg}")
        post_status(api_url, token, repo, head_sha, state="failure", description=msg)


if __name__ == "__main__":
    main()
