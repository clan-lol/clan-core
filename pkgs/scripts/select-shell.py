import argparse
import json
import pathlib
import subprocess
import sys

parser = argparse.ArgumentParser(description="Select a devshell")
parser.add_argument("shell", help="the name of the devshell to select", nargs="?")
parser.add_argument("--list", action="store_true", help="list available devshells")
args = parser.parse_args()

selected_shell_file = pathlib.Path(".direnv/selected-shell")

if not args.list and not args.shell:
    parser.print_help()
    exit(0)
if args.list:
    flake_show = subprocess.run(
        ["nix", "flake", "show", "--json", "--no-write-lock-file"],
        stdout=subprocess.PIPE,
    )
    data = json.loads(flake_show.stdout.decode())
    print("Available devshells:")
    print("\n".join(data["devShells"]["x86_64-linux"].keys()))
    exit(0)
if selected_shell_file.exists():
    with open(selected_shell_file) as f:
        current_shell = f.read().strip()
else:
    current_shell = ""

if current_shell == args.shell:
    print(f"{args.shell} devshell already selected. No changes made.")
    sys.exit(0)

with open(selected_shell_file, "w") as f:
    f.write(args.shell)

print(f"{args.shell} devshell selected")
