#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

SRC=clan_cli/tests/test_vars.py
DIR=clan_cli/tests
GEN_TEST=clan_lib/vars/generator_test.py

# --- Step 1: Extract invalidate_flake_cache to helpers ---
cat > "$DIR/helpers/flake_cache.py" << 'IMPORTS'
import time
from pathlib import Path

from clan_lib.nix import run


IMPORTS
sed -n '54,62p' "$SRC" >> "$DIR/helpers/flake_cache.py"
echo "" >> "$DIR/helpers/flake_cache.py"

# --- Step 2: Move test_dependencies_as_files to generator_test.py ---
# Add needed import
sed -i 's/from .generator import filter_machine_specific_attrs/from .generator import dependencies_as_dir, filter_machine_specific_attrs/' "$GEN_TEST"
# Append test function
echo "" >> "$GEN_TEST"
echo "" >> "$GEN_TEST"
sed -n '65,86p' "$SRC" >> "$GEN_TEST"
echo "" >> "$GEN_TEST"

# --- Step 3: Create test_vars_generate.py (8 tests) ---
sed -n '1,40p'     "$SRC"  > "$DIR/test_vars_generate.py"
echo ""                    >> "$DIR/test_vars_generate.py"
echo ""                    >> "$DIR/test_vars_generate.py"
sed -n '43,51p'    "$SRC" >> "$DIR/test_vars_generate.py"  # test_import_from_cli
echo ""                    >> "$DIR/test_vars_generate.py"
echo ""                    >> "$DIR/test_vars_generate.py"
sed -n '89,342p'   "$SRC" >> "$DIR/test_vars_generate.py"  # test_generate_public_and_secret_vars
echo ""                    >> "$DIR/test_vars_generate.py"
echo ""                    >> "$DIR/test_vars_generate.py"
sed -n '344,449p'  "$SRC" >> "$DIR/test_vars_generate.py"  # test_generate_secret_var_sops_with_default_group (incl TODO comment)
echo ""                    >> "$DIR/test_vars_generate.py"
echo ""                    >> "$DIR/test_vars_generate.py"
sed -n '451,563p'  "$SRC" >> "$DIR/test_vars_generate.py"  # test_generate_shared_secret_sops
echo ""                    >> "$DIR/test_vars_generate.py"
echo ""                    >> "$DIR/test_vars_generate.py"
sed -n '565,682p'  "$SRC" >> "$DIR/test_vars_generate.py"  # test_generate_secret_var_password_store
echo ""                    >> "$DIR/test_vars_generate.py"
echo ""                    >> "$DIR/test_vars_generate.py"
sed -n '684,745p'  "$SRC" >> "$DIR/test_vars_generate.py"  # test_generate_secret_for_multiple_machines
echo ""                    >> "$DIR/test_vars_generate.py"
echo ""                    >> "$DIR/test_vars_generate.py"
sed -n '1588,1666p' "$SRC" >> "$DIR/test_vars_generate.py" # test_stdout_of_generate
echo ""                    >> "$DIR/test_vars_generate.py"
echo ""                    >> "$DIR/test_vars_generate.py"
sed -n '1717,1734p' "$SRC" >> "$DIR/test_vars_generate.py" # test_create_sops_age_secrets
echo ""                    >> "$DIR/test_vars_generate.py"

# --- Step 4: Create test_vars_prompts.py (4 tests) ---
sed -n '1,40p'     "$SRC"  > "$DIR/test_vars_prompts.py"
echo ""                    >> "$DIR/test_vars_prompts.py"
echo ""                    >> "$DIR/test_vars_prompts.py"
sed -n '747,840p'  "$SRC" >> "$DIR/test_vars_prompts.py"   # test_prompt
echo ""                    >> "$DIR/test_vars_prompts.py"
echo ""                    >> "$DIR/test_vars_prompts.py"
sed -n '842,1123p' "$SRC" >> "$DIR/test_vars_prompts.py"   # test_prompt_prefill_on_regeneration
echo ""                    >> "$DIR/test_vars_prompts.py"
echo ""                    >> "$DIR/test_vars_prompts.py"
sed -n '1465,1520p' "$SRC" >> "$DIR/test_vars_prompts.py"  # test_api_set_prompts
echo ""                    >> "$DIR/test_vars_prompts.py"
echo ""                    >> "$DIR/test_vars_prompts.py"
sed -n '1522,1586p' "$SRC" >> "$DIR/test_vars_prompts.py"  # test_get_generator_prompt_previous_values
echo ""                    >> "$DIR/test_vars_prompts.py"

# --- Step 5: Create test_vars_errors.py (7 tests) ---
sed -n '1,40p'     "$SRC"  > "$DIR/test_vars_errors.py"
echo ""                    >> "$DIR/test_vars_errors.py"
echo ""                    >> "$DIR/test_vars_errors.py"
sed -n '1125,1146p' "$SRC" >> "$DIR/test_vars_errors.py"   # test_non_existing_dependency_raises_error
echo ""                    >> "$DIR/test_vars_errors.py"
echo ""                    >> "$DIR/test_vars_errors.py"
sed -n '1148,1169p' "$SRC" >> "$DIR/test_vars_errors.py"   # test_generator_script_missing_output_file
echo ""                    >> "$DIR/test_vars_errors.py"
echo ""                    >> "$DIR/test_vars_errors.py"
sed -n '1171,1188p' "$SRC" >> "$DIR/test_vars_errors.py"   # test_generator_script_fails_with_nonzero_exit
echo ""                    >> "$DIR/test_vars_errors.py"
echo ""                    >> "$DIR/test_vars_errors.py"
sed -n '1190,1214p' "$SRC" >> "$DIR/test_vars_errors.py"   # test_circular_dependency_raises_error
echo ""                    >> "$DIR/test_vars_errors.py"
echo ""                    >> "$DIR/test_vars_errors.py"
sed -n '1216,1245p' "$SRC" >> "$DIR/test_vars_errors.py"   # test_shared_vars_must_never_depend_on_machine_specific_vars
echo ""                    >> "$DIR/test_vars_errors.py"
echo ""                    >> "$DIR/test_vars_errors.py"
sed -n '1668,1715p' "$SRC" >> "$DIR/test_vars_errors.py"   # test_fails_when_files_are_left_from_other_backend
echo ""                    >> "$DIR/test_vars_errors.py"
echo ""                    >> "$DIR/test_vars_errors.py"
sed -n '2165,2204p' "$SRC" >> "$DIR/test_vars_errors.py"   # test_shared_generator_conflicting_definition_raises_error
echo ""                    >> "$DIR/test_vars_errors.py"

# --- Step 6: Create test_vars_shared.py (5 tests) ---
sed -n '1,40p'     "$SRC"  > "$DIR/test_vars_shared.py"
echo ""                    >> "$DIR/test_vars_shared.py"
echo ""                    >> "$DIR/test_vars_shared.py"
sed -n '1247,1320p' "$SRC" >> "$DIR/test_vars_shared.py"   # test_shared_vars_regeneration
echo ""                    >> "$DIR/test_vars_shared.py"
echo ""                    >> "$DIR/test_vars_shared.py"
sed -n '1322,1392p' "$SRC" >> "$DIR/test_vars_shared.py"   # test_multi_machine_shared_vars
echo ""                    >> "$DIR/test_vars_shared.py"
echo ""                    >> "$DIR/test_vars_shared.py"
sed -n '1394,1463p' "$SRC" >> "$DIR/test_vars_shared.py"   # test_add_machine_to_existing_shared_secret
echo ""                    >> "$DIR/test_vars_shared.py"
echo ""                    >> "$DIR/test_vars_shared.py"
sed -n '1784,1866p' "$SRC" >> "$DIR/test_vars_shared.py"   # test_share_mode_switch_regenerates_secret
echo ""                    >> "$DIR/test_vars_shared.py"
echo ""                    >> "$DIR/test_vars_shared.py"
sed -n '2206,2252p' "$SRC" >> "$DIR/test_vars_shared.py"   # test_shared_generator_allows_machine_specific_differences
echo ""                    >> "$DIR/test_vars_shared.py"

# --- Step 7: Create test_vars_cache.py (6 tests) ---
sed -n '1,40p'     "$SRC"  > "$DIR/test_vars_cache.py"
# Add invalidate_flake_cache import (needed by 3 tests in this file)
echo "from clan_cli.tests.helpers.flake_cache import invalidate_flake_cache" >> "$DIR/test_vars_cache.py"
echo ""                    >> "$DIR/test_vars_cache.py"
echo ""                    >> "$DIR/test_vars_cache.py"
sed -n '1736,1782p' "$SRC" >> "$DIR/test_vars_cache.py"    # test_invalidation
echo ""                    >> "$DIR/test_vars_cache.py"
echo ""                    >> "$DIR/test_vars_cache.py"
sed -n '1868,1979p' "$SRC" >> "$DIR/test_vars_cache.py"    # test_generate_secret_var_password_store_minimal_select_calls
echo ""                    >> "$DIR/test_vars_cache.py"
echo ""                    >> "$DIR/test_vars_cache.py"
sed -n '1981,2081p' "$SRC" >> "$DIR/test_vars_cache.py"    # test_generate_secret_var_sops_minimal_select_calls
echo ""                    >> "$DIR/test_vars_cache.py"
echo ""                    >> "$DIR/test_vars_cache.py"
sed -n '2083,2163p' "$SRC" >> "$DIR/test_vars_cache.py"    # test_cache_misses_for_vars_operations
echo ""                    >> "$DIR/test_vars_cache.py"
echo ""                    >> "$DIR/test_vars_cache.py"
sed -n '2254,2341p' "$SRC" >> "$DIR/test_vars_cache.py"    # test_dynamic_invalidation
echo ""                    >> "$DIR/test_vars_cache.py"
echo ""                    >> "$DIR/test_vars_cache.py"
sed -n '2343,2417p' "$SRC" >> "$DIR/test_vars_cache.py"    # test_get_generators_only_decrypts_requested_machines
echo ""                    >> "$DIR/test_vars_cache.py"

# --- Step 8: Update test_vars_age.py import ---
sed -i 's|from clan_cli.tests.test_vars import invalidate_flake_cache|from clan_cli.tests.helpers.flake_cache import invalidate_flake_cache|' "$DIR/test_vars_age.py"

# --- Step 9: Clean up unused imports and fix sorting with ruff ---
ruff check --fix --select F401,I001 \
  "$DIR/test_vars_generate.py" \
  "$DIR/test_vars_prompts.py" \
  "$DIR/test_vars_errors.py" \
  "$DIR/test_vars_shared.py" \
  "$DIR/test_vars_cache.py" \
  "$GEN_TEST" || true

ruff format \
  "$DIR/test_vars_generate.py" \
  "$DIR/test_vars_prompts.py" \
  "$DIR/test_vars_errors.py" \
  "$DIR/test_vars_shared.py" \
  "$DIR/test_vars_cache.py" \
  "$DIR/helpers/flake_cache.py" \
  "$GEN_TEST"

# --- Step 10: Add missing Path import to generator_test.py ---
sed -i '1i from pathlib import Path' "$GEN_TEST"
ruff check --fix --select I001 "$GEN_TEST" || true
ruff format "$GEN_TEST"

# --- Step 11: Delete original ---
rm "$SRC"

echo "Done. Verify with: pytest --collect-only clan_cli/tests/test_vars_*.py clan_lib/vars/generator_test.py"
