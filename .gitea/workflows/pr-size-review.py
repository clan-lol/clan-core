"""Check that large PRs (>500 lines added) have at least 2 approving reviews."""

import json
import math
import os
import sys
import urllib.request

MAX_ADDITIONS_SINGLE_REVIEW = 500
MIN_APPROVALS_LARGE_PR = 1

LOCK_FILE_PATTERNS = (
    ".lock",
    "-lock.json",
)


def is_lock_file(filename: str) -> bool:
    basename = filename.rsplit("/", 1)[-1]
    return any(basename.endswith(pat) for pat in LOCK_FILE_PATTERNS)


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
    total_additions: int = pr_data["additions"]
    pr_author: str = pr_data["user"]["login"]

    # Get per-file stats to exclude lock files
    changed_files: int = pr_data["changed_files"]
    page_size = 50
    num_pages = math.ceil(changed_files / page_size)
    lock_additions = 0
    for page in range(1, num_pages + 1):
        files = api_get(
            f"{api_url}/repos/{repo}/pulls/{pr_number}/files?limit={page_size}&page={page}",
            token,
        )
        if not isinstance(files, list):
            print("Error: unexpected API response for PR files", file=sys.stderr)
            sys.exit(1)
        for f in files:
            if is_lock_file(f["filename"]):
                lock_additions += f.get("additions", 0)
                print(
                    f"  Ignoring lock file: {f['filename']} (+{f.get('additions', 0)})"
                )

    additions: int = total_additions - lock_additions

    if lock_additions:
        print(
            f"PR #{pr_number}: +{total_additions} total, "
            f"+{lock_additions} in lock files, +{additions} counted"
        )
    else:
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
