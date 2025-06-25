import argparse
import contextlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

# push origin HEAD:refs/for/main
# HEAD: The target branch
# origin: The target repository (not a fork!)
# HEAD: The local branch containing the changes you are proposing
TARGET_REMOTE_REPOSITORY = "origin"
DEFAULT_TARGET_BRANCH = "main"


def get_gitea_api_url(remote: str = "origin") -> str:
    """Parse the gitea api url, this parser is fairly naive, but should work for most setups"""
    exit_code, remote_url, error = run_git_command(["git", "remote", "get-url", remote])

    if exit_code != 0:
        print(f"Error getting remote URL for '{remote}': {error}")
        sys.exit(1)

    # Parse different remote URL formats
    # SSH formats: git@git.clan.lol:clan/clan-core.git or gitea@git.clan.lol:clan/clan-core.git
    # HTTPS format: https://git.clan.lol/clan/clan-core.git

    if (
        "@" in remote_url
        and ":" in remote_url
        and not remote_url.startswith("https://")
    ):
        # SSH format: [user]@git.clan.lol:clan/clan-core.git
        host_and_path = remote_url.split("@")[1]  # git.clan.lol:clan/clan-core.git
        host = host_and_path.split(":")[0]  # git.clan.lol
        repo_path = host_and_path.split(":")[1]  # clan/clan-core.git
        if repo_path.endswith(".git"):
            repo_path = repo_path[:-4]  # clan/clan-core
    elif remote_url.startswith("https://"):
        # HTTPS format: https://git.clan.lol/clan/clan-core.git
        url_parts = remote_url.replace("https://", "").split("/")
        host = url_parts[0]  # git.clan.lol
        repo_path = "/".join(url_parts[1:])  # clan/clan-core.git
        if repo_path.endswith(".git"):
            repo_path = repo_path.removesuffix(".git")  # clan/clan-core
    else:
        print(f"Unsupported remote URL format: {remote_url}")
        sys.exit(1)

    api_url = f"https://{host}/api/v1/repos/{repo_path}/pulls"
    return api_url


def fetch_open_prs(remote: str = "origin") -> list[dict]:
    """Fetch open pull requests from the Gitea API."""
    api_url = get_gitea_api_url(remote)

    try:
        with urllib.request.urlopen(f"{api_url}?state=open") as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.URLError as e:
        print(f"Error fetching PRs from {api_url}: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        sys.exit(1)


def get_repo_info_from_api_url(api_url: str) -> tuple[str, str]:
    """Extract repository owner and name from API URL."""
    # api_url format: https://git.clan.lol/api/v1/repos/clan/clan-core/pulls
    parts = api_url.split("/")
    if len(parts) >= 6 and "repos" in parts:
        repo_index = parts.index("repos")
        if repo_index + 2 < len(parts):
            owner = parts[repo_index + 1]
            repo_name = parts[repo_index + 2]
            return owner, repo_name
    msg = f"Invalid API URL format: {api_url}"
    raise ValueError(msg)


def fetch_pr_statuses(
    repo_owner: str, repo_name: str, commit_sha: str, host: str
) -> list[dict]:
    """Fetch CI statuses for a specific commit SHA."""
    status_url = (
        f"https://{host}/api/v1/repos/{repo_owner}/{repo_name}/statuses/{commit_sha}"
    )

    try:
        request = urllib.request.Request(status_url)
        with urllib.request.urlopen(request, timeout=3) as response:
            data = json.loads(response.read().decode())
            return data
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        # Fail silently for individual status requests to keep listing fast
        return []


def get_latest_status_by_context(statuses: list[dict]) -> dict[str, str]:
    """Group statuses by context and return the latest status for each context."""
    context_statuses = {}

    for status in statuses:
        context = status.get("context", "unknown")
        created_at = status.get("created_at", "")
        status_state = status.get("status", "unknown")

        if (
            context not in context_statuses
            or created_at > context_statuses[context]["created_at"]
        ):
            context_statuses[context] = {
                "status": status_state,
                "created_at": created_at,
            }

    return {context: info["status"] for context, info in context_statuses.items()}


def status_to_emoji(status: str) -> str:
    """Convert status string to emoji."""
    status_map = {"success": "✅", "failure": "❌", "pending": "🟡", "error": "❓"}
    return status_map.get(status.lower(), "❓")


def create_osc8_link(url: str, text: str) -> str:
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


def format_pr_with_status(pr: dict, remote: str = "origin") -> str:
    """Format PR title with status emojis and OSC8 link."""
    title = pr["title"]
    pr_url = pr.get("html_url", "")

    commit_sha = pr.get("head", {}).get("sha")
    if not commit_sha:
        if pr_url:
            return create_osc8_link(pr_url, title)
        return title

    try:
        api_url = get_gitea_api_url(remote)
        repo_owner, repo_name = get_repo_info_from_api_url(api_url)

        host = api_url.split("/")[2]

        statuses = fetch_pr_statuses(repo_owner, repo_name, commit_sha, host)
        if not statuses:
            if pr_url:
                return create_osc8_link(pr_url, title)
            return title

        latest_statuses = get_latest_status_by_context(statuses)

        emojis = [status_to_emoji(status) for status in latest_statuses.values()]
        formatted_title = f"{title} {' '.join(emojis)}" if emojis else title

        return create_osc8_link(pr_url, formatted_title) if pr_url else formatted_title

    except (ValueError, IndexError):
        # If there's any error in processing, just return the title with link if available
        if pr_url:
            return create_osc8_link(pr_url, title)

    return title


def run_git_command(command: list) -> tuple[int, str, str]:
    """Run a git command and return exit code, stdout, and stderr."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def get_current_branch_name() -> str:
    exit_code, branch_name, error = run_git_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    )

    if exit_code != 0:
        print(f"Error getting branch name: {error}")
        sys.exit(1)

    return branch_name.strip()


def get_latest_commit_info() -> tuple[str, str]:
    """Get the title and body of the latest commit."""
    exit_code, commit_msg, error = run_git_command(
        ["git", "log", "-1", "--pretty=format:%B"]
    )

    if exit_code != 0:
        print(f"Error getting commit info: {error}")
        sys.exit(1)

    lines = commit_msg.strip().split("\n")
    title = lines[0].strip() if lines else ""

    body_lines = []
    for line in lines[1:]:
        if body_lines or line.strip():
            body_lines.append(line)

    body = "\n".join(body_lines).strip()

    return title, body


def get_commits_since_main() -> list[tuple[str, str]]:
    """Get all commits since main as (title, body) tuples."""
    exit_code, commit_log, error = run_git_command(
        [
            "git",
            "log",
            "main..HEAD",
            "--no-merges",
            "--pretty=format:%s|%b|---END---",
        ]
    )

    if exit_code != 0:
        print(f"Error getting commits since main: {error}")
        return []

    if not commit_log:
        return []

    commits = []
    commit_messages = commit_log.split("---END---")

    for commit_msg in commit_messages:
        commit_msg = commit_msg.strip()
        if not commit_msg:
            continue

        parts = commit_msg.split("|")
        if len(parts) < 2:
            continue

        title = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ""

        if not title:
            continue

        commits.append((title, body))

    return commits


def open_editor_for_pr() -> tuple[str, str]:
    """Open editor to get PR title and description. First line is title, rest is description."""
    commits_since_main = get_commits_since_main()

    with tempfile.NamedTemporaryFile(
        mode="w+", suffix="COMMIT_EDITMSG", delete=False
    ) as temp_file:
        temp_file.write("\n")
        temp_file.write("# Please enter the PR title on the first line.\n")
        temp_file.write("# Lines starting with '#' will be ignored.\n")
        temp_file.write("# The first line will be used as the PR title.\n")
        temp_file.write("# Everything else will be used as the PR description.\n")
        temp_file.write(
            "# To abort creation of the PR, close editor with an error code.\n"
        )
        temp_file.write("# In vim for example you can use :cq!\n")
        temp_file.write("#\n")
        temp_file.write("# All commits since main:\n")
        temp_file.write("#\n")
        for i, (title, body) in enumerate(commits_since_main, 1):
            temp_file.write(f"# Commit {i}:\n")
            temp_file.write(f"# {title}\n")
            if body:
                for line in body.split("\n"):
                    temp_file.write(f"# {line}\n")
            temp_file.write("#\n")
        temp_file.flush()
        temp_file_path = temp_file.name

    try:
        editor = os.environ.get("EDITOR", "vim")

        exit_code = subprocess.call([editor, temp_file_path])

        if exit_code != 0:
            print(f"Editor exited with code {exit_code}.")
            print("AGit PR creation has been aborted.")
            sys.exit(1)

        with Path(temp_file_path).open() as f:
            content = f.read()

        lines = []
        for line in content.split("\n"):
            if not line.lstrip().startswith("#"):
                lines.append(line)

        cleaned_content = "\n".join(lines).strip()

        if not cleaned_content:
            print("No content provided, aborting.")
            sys.exit(0)

        content_lines = cleaned_content.split("\n")
        title = content_lines[0].strip()

        if not title:
            print("No title provided, aborting.")
            sys.exit(0)

        description_lines = []
        for line in content_lines[1:]:
            if description_lines or line.strip():
                description_lines.append(line)

        description = "\n".join(description_lines).strip()

        return title, description

    finally:
        with contextlib.suppress(OSError):
            Path(temp_file_path).unlink()


def create_agit_push(
    remote: str = "origin",
    branch: str = "main",
    topic: str | None = None,
    title: str | None = None,
    description: str | None = None,
    force_push: bool = False,
    local_branch: str = "HEAD",
) -> None:
    if topic is None:
        if title is not None:
            topic = title
        else:
            topic = get_current_branch_name()

    refspec = f"{local_branch}:refs/for/{branch}"
    push_cmd = ["git", "push", remote, refspec]

    push_cmd.extend(["-o", f"topic={topic}"])

    if title:
        push_cmd.extend(["-o", f"title={title}"])

    if description:
        escaped_desc = description.rstrip("\n").replace('"', '\\"')
        push_cmd.extend(["-o", f"description={escaped_desc}"])

    if force_push:
        push_cmd.extend(["-o", "force-push"])

    if description:
        print(
            f"  Description: {description[:50]}..."
            if len(description) > 50
            else f"  Description: {description}"
        )
    print()

    exit_code, stdout, stderr = run_git_command(push_cmd)

    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    if exit_code != 0:
        print("\nPush failed!")
        sys.exit(exit_code)
    else:
        print("\nPush successful!")


def cmd_create(args: argparse.Namespace) -> None:
    """Handle the create subcommand."""
    title = args.title
    description = args.description

    if not args.auto and (title is None or description is None):
        editor_title, editor_description = open_editor_for_pr()
        if title is None:
            title = editor_title
        if description is None:
            description = editor_description

    create_agit_push(
        remote=args.remote,
        branch=args.branch,
        topic=args.topic,
        title=title,
        description=description,
        force_push=args.force,
        local_branch=args.local_branch,
    )


def cmd_list(args: argparse.Namespace) -> None:
    """Handle the list subcommand."""
    prs = fetch_open_prs(args.remote)

    if not prs:
        print("No open AGit pull requests found.")
        return

    # This is the only way I found to query the actual AGit PRs
    # Gitea doesn't seem to have an actual api endpoint for them
    filtered_prs = [pr for pr in prs if pr.get("head", {}).get("label", "") == ""]

    if not filtered_prs:
        print("No open AGit pull requests found.")
        return

    for pr in filtered_prs:
        formatted_pr = format_pr_with_status(pr, args.remote)
        print(formatted_pr)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agit",
        description="AGit utility for creating and pulling PRs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
The defaults that are assumed are:
TARGET_REMOTE_REPOSITORY = {TARGET_REMOTE_REPOSITORY}
DEFAULT_TARGET_BRANCH = {DEFAULT_TARGET_BRANCH}

Examples:
  $ agit create
  Opens editor to compose PR title and description (first line is title, rest is body)

  $ agit create --auto
  Creates PR using latest commit message automatically

  $ agit create --topic "my-feature"
  Set a custom topic.

  $ agit create --force
  Force push to a certain topic

  $ agit list
  Lists all open pull requests for the current repository
        """,
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Commands")

    create_parser = subparsers.add_parser(
        "create",
        aliases=["c"],
        help="Create an AGit PR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  $ agit create
  Opens editor to compose PR title and description (first line is title, rest is body).

  $ agit create --auto
  Creates PR using latest commit message automatically (old behavior).

  $ agit create --topic "my-feature"
  Set a custom topic.

  $ agit create --force
  Force push to a certain topic
        """,
    )

    list_parser = subparsers.add_parser(
        "list",
        aliases=["l"],
        help="List open AGit pull requests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  $ agit list
  Lists all open AGit PRs for the current repository.

  $ agit list --remote upstream
  Lists PRs using the 'upstream' remote instead of '{TARGET_REMOTE_REPOSITORY}'.
        """,
    )

    list_parser.add_argument(
        "-r",
        "--remote",
        default=TARGET_REMOTE_REPOSITORY,
        help=f"Git remote to use for fetching PRs (default: {TARGET_REMOTE_REPOSITORY})",
    )

    create_parser.add_argument(
        "-r",
        "--remote",
        default=TARGET_REMOTE_REPOSITORY,
        help=f"Git remote to push to (default: {TARGET_REMOTE_REPOSITORY})",
    )

    create_parser.add_argument(
        "-b",
        "--branch",
        default=DEFAULT_TARGET_BRANCH,
        help=f"Target branch for the PR (default: {DEFAULT_TARGET_BRANCH})",
    )

    create_parser.add_argument(
        "-l",
        "--local-branch",
        default="HEAD",
        help="Local branch to push (default: HEAD)",
    )

    create_parser.add_argument(
        "-t", "--topic", help="Set PR topic (default: current branch name)"
    )

    create_parser.add_argument(
        "--title", help="Set the PR title (default: last commit title)"
    )

    create_parser.add_argument(
        "--description", help="Override the PR description (default: commit body)"
    )

    create_parser.add_argument(
        "-f", "--force", action="store_true", help="Force push the changes"
    )

    create_parser.add_argument(
        "-a",
        "--auto",
        action="store_true",
        help="Skip editor and use commit message automatically",
    )

    create_parser.set_defaults(func=cmd_create)
    list_parser.set_defaults(func=cmd_list)
    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
