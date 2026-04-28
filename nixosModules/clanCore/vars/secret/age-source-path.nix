# Compute the on-disk path of an age-encrypted vars secret produced by
# clan_lib/vars/secret_modules/age.py:secret_path.
#
# Both sides MUST stay in lockstep. The contract is pinned by
# eval-tests/age-source-path.nix, which evaluates this function against
# real on-disk fixtures and asserts every fixture is reachable.
#
# Layout:
#   per-machine: {clanDir}/secrets/clan-vars/per-machine/{machine}/{generator}/{name}/{name}.age
#   shared:      {clanDir}/secrets/clan-vars/shared/{generator}/{name}/{name}.age
#   per-export:  {clanDir}/secrets/clan-vars/per-export/{export}/{generator}/{name}/{name}.age
#
# The trailing `{name}/{name}.age` shape is intentional: the directory
# `{name}/` mirrors the per-file output directory used by every backend
# (sops `secret`, in_repo `value`, age `{name}.age`).
clanDir: rel_dir: fileName:
clanDir + "/secrets/clan-vars/${rel_dir}/${fileName}/${fileName}.age"
