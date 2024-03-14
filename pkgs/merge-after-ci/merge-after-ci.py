import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--reviewers", nargs="*", default=[])
parser.add_argument("--no-review", action="store_true")
parser.add_argument("args", nargs="*")
args = parser.parse_args()

# complain if neither --reviewers nor --no-review is given
if not args.reviewers and not args.no_review:
    parser.error("either --reviewers or --no-review must be given")

subprocess.run(
    [
        "tea-create-pr",
        "origin",
        "main",
        "--assignees",
        ",".join(["clan-bot", *args.reviewers]),
        *(["--labels", "needs-review"] if not args.no_review else []),
        *args.args,
    ]
)
