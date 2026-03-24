#!/usr/bin/env bash
# Reverse of split_test_vars.sh: recreates test_vars.py from the split files,
# then removes the split artifacts.
set -euo pipefail

cd "$(dirname "$0")"

DIR=clan_cli/tests
GEN_TEST=clan_lib/vars/generator_test.py
OUT="$DIR/test_vars.py"

# --- Step 1: Reconstruct test_vars.py from the split files ---
python3 - "$DIR" "$GEN_TEST" "$OUT" << 'PYEOF'
import re
import sys
from pathlib import Path

dir_path = sys.argv[1]
gen_test = sys.argv[2]
out_path = sys.argv[3]


def extract_function(filepath: str, funcname: str) -> str:
    """Extract a named function and its preceding decorators/comments from a file.

    Walks backwards from the def line to capture @decorators and # comments,
    then walks forward to the next top-level construct or EOF.
    """
    lines = Path(filepath).read_text().splitlines(keepends=True)

    # Find the def line
    def_idx = None
    for i, line in enumerate(lines):
        if re.match(rf"^def {re.escape(funcname)}\(", line):
            def_idx = i
            break

    if def_idx is None:
        raise ValueError(f"{funcname} not found in {filepath}")

    # Walk backwards for decorators and comments attached to this function
    start = def_idx
    while start > 0:
        prev = lines[start - 1].rstrip()
        if prev.startswith("@") or prev.startswith("#"):
            start -= 1
        else:
            break

    # Walk forward to find end of function body
    # Stop at the next top-level construct: def, class, @decorator, or # comment
    # (column-0 comments belong to the next function, not the current one)
    end = def_idx + 1
    while end < len(lines):
        line = lines[end]
        if line.strip() and not line[0].isspace():
            if re.match(r"^(def |class |@|#)", line):
                break
        end += 1

    # Strip trailing blank lines
    while end > start and not lines[end - 1].strip():
        end -= 1

    return "".join(lines[start:end])


# Import header from the original test_vars.py (lines 1-40)
IMPORT_HEADER = """\
import argparse
import importlib
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pexpect  # type: ignore[import-untyped]
import pytest
from clan_cli.secrets.secrets import decrypt_secret
from clan_cli.tests.age_keys import SopsSetup
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config
from clan_cli.tests.helpers import cli
from clan_cli.vars.check import check_vars
from clan_cli.vars.generate import generate_command
from clan_cli.vars.get import get_machine_var
from clan_cli.vars.public_modules import in_repo
from clan_cli.vars.secret_modules import password_store, sops
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix import current_system, nix_config, nix_eval, run
from clan_lib.nix_selectors import get_machine_prefix, vars_generators_metadata
from clan_lib.vars._types import GeneratorId, PerMachine, Shared
from clan_lib.vars.generate import (
    GeneratorPromptIdentifier,
    get_generator_prompt_previous_values,
    get_generators,
    run_generators,
)
from clan_lib.vars.generator import (
    Generator,
    dependencies_as_dir,
)
from clan_lib.vars.list import stringify_all_vars
from clan_lib.vars.set import set_var
"""

# Functions in original test_vars.py order, with their source files
gen = f"{dir_path}/test_vars_generate.py"
prompts = f"{dir_path}/test_vars_prompts.py"
errors = f"{dir_path}/test_vars_errors.py"
shared = f"{dir_path}/test_vars_shared.py"
cache = f"{dir_path}/test_vars_cache.py"
flake_cache = f"{dir_path}/helpers/flake_cache.py"

FUNCTIONS = [
    (gen,        "test_import_from_cli"),
    (flake_cache, "invalidate_flake_cache"),
    (gen_test,   "test_dependencies_as_files"),
    (gen,        "test_generate_public_and_secret_vars"),
    (gen,        "test_generate_secret_var_sops_with_default_group"),
    (gen,        "test_generate_shared_secret_sops"),
    (gen,        "test_generate_secret_var_password_store"),
    (gen,        "test_generate_secret_for_multiple_machines"),
    (prompts,    "test_prompt"),
    (prompts,    "test_prompt_prefill_on_regeneration"),
    (errors,     "test_non_existing_dependency_raises_error"),
    (errors,     "test_generator_script_missing_output_file"),
    (errors,     "test_generator_script_fails_with_nonzero_exit"),
    (errors,     "test_circular_dependency_raises_error"),
    (errors,     "test_shared_vars_must_never_depend_on_machine_specific_vars"),
    (shared,     "test_shared_vars_regeneration"),
    (shared,     "test_multi_machine_shared_vars"),
    (shared,     "test_add_machine_to_existing_shared_secret"),
    (prompts,    "test_api_set_prompts"),
    (prompts,    "test_get_generator_prompt_previous_values"),
    (gen,        "test_stdout_of_generate"),
    (errors,     "test_fails_when_files_are_left_from_other_backend"),
    (gen,        "test_create_sops_age_secrets"),
    (cache,      "test_invalidation"),
    (shared,     "test_share_mode_switch_regenerates_secret"),
    (cache,      "test_generate_secret_var_password_store_minimal_select_calls"),
    (cache,      "test_generate_secret_var_sops_minimal_select_calls"),
    (cache,      "test_cache_misses_for_vars_operations"),
    (errors,     "test_shared_generator_conflicting_definition_raises_error"),
    (shared,     "test_shared_generator_allows_machine_specific_differences"),
    (cache,      "test_dynamic_invalidation"),
    (cache,      "test_get_generators_only_decrypts_requested_machines"),
]

# Build the output
parts = [IMPORT_HEADER]
for filepath, funcname in FUNCTIONS:
    parts.append("\n")
    parts.append(extract_function(filepath, funcname))

output = "".join(parts)
# Ensure single trailing newline
output = output.rstrip("\n") + "\n"

Path(out_path).write_text(output)
print(f"Reconstructed {out_path} ({output.count(chr(10))} lines)")
PYEOF

# --- Step 2: Remove split test files ---
rm -f "$DIR/test_vars_generate.py" \
      "$DIR/test_vars_prompts.py" \
      "$DIR/test_vars_errors.py" \
      "$DIR/test_vars_shared.py" \
      "$DIR/test_vars_cache.py" \
      "$DIR/helpers/flake_cache.py"

# --- Step 3: Revert generator_test.py ---
# Remove test_dependencies_as_files (appended after blank lines at end)
# and revert imports to original state
python3 - "$GEN_TEST" << 'PYEOF'
import re
from pathlib import Path
import sys

filepath = sys.argv[1]
text = Path(filepath).read_text()

# Remove the appended test_dependencies_as_files function
# It starts after two blank lines following the last original test
text = re.sub(r'\n\n\ndef test_dependencies_as_files\(.*', '', text, flags=re.DOTALL)

# Revert import: remove dependencies_as_dir
text = text.replace(
    "from .generator import dependencies_as_dir, filter_machine_specific_attrs",
    "from .generator import filter_machine_specific_attrs",
)

# Remove the added "from pathlib import Path" line
text = text.replace("from pathlib import Path\n", "", 1)

# Ensure single trailing newline
text = text.rstrip("\n") + "\n"

Path(filepath).write_text(text)
print(f"Reverted {filepath}")
PYEOF

# --- Step 4: Revert test_vars_age.py import ---
sed -i 's|from clan_cli.tests.helpers.flake_cache import invalidate_flake_cache|from clan_cli.tests.test_vars import invalidate_flake_cache|' "$DIR/test_vars_age.py"

# --- Step 5: Format reconstructed file ---
ruff format "$OUT" "$GEN_TEST"

echo "Done. Verify with: pytest --collect-only $DIR/test_vars.py"
