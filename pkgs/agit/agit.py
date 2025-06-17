import argparse
import contextlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# push origin HEAD:refs/for/main
# HEAD: The target branch
# origin: The target repository (not a fork!)
# HEAD: The local branch containing the changes you are proposing
TARGET_REMOTE_REPOSITORY = "origin"
DEFAULT_TARGET_BRANCH = "main"


def run_git_command(command: list) -> tuple[int, str, str]:
    """Run a git command and return exit code, stdout, and stderr."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


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


def open_editor_for_pr() -> tuple[str, str]:
    """Open editor to get PR title and description. First line is title, rest is description."""
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete=False
    ) as temp_file:
        temp_file.write("\n")
        temp_file.write("# Please enter the PR title on the first line.\n")
        temp_file.write("# Lines starting with '#' will be ignored.\n")
        temp_file.write("# The first line will be used as the PR title.\n")
        temp_file.write("# Everything else will be used as the PR description.\n")
        temp_file.write("#\n")
        temp_file.flush()
        temp_file_path = temp_file.name

    try:
        editor = os.environ.get("EDITOR", "vim")

        exit_code = subprocess.call([editor, temp_file_path])

        if exit_code != 0:
            print(f"Editor exited with code {exit_code}")
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
            commit_title, _ = get_latest_commit_info()
            topic = commit_title

    refspec = f"{local_branch}:refs/for/{branch}"
    push_cmd = ["git", "push", remote, refspec]

    push_cmd.extend(["-o", f"topic={topic}"])

    if title:
        push_cmd.extend(["-o", f"title={title}"])

    if description:
        escaped_desc = description.replace('"', '\\"')
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
  Opens editor to compose PR title and description (first line is title, rest is body).

  $ agit create --auto
  Creates PR using latest commit message automatically (old behavior).

  $ agit create --topic "my-feature"
  Set a custom topic.

  $ agit create --force
  Force push to a certain topic
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
        "-t", "--topic", help="Set PR topic (default: last commit title)"
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
