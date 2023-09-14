import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))

pytest_plugins = [
    "api",
    "temporary_dir",
    "clan_flake",
    "root",
    "age_keys",
    "sshd",
    "command",
    "ports",
    "host_group",
    "machine_flake",
]
