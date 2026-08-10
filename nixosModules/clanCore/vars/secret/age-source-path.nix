# On-disk path of an age-encrypted vars secret.
# Mirrors clan_lib/vars/secret_modules/age.py:secret_path.
# Pinned by eval-tests/age-source-path.nix against real fixtures.
#
# {clanDir}/secrets/clan-vars/{rel_dir}/{name}/{name}.age
#
# rel_dir is per-machine/{machine}/{gen}, shared/{gen}, or per-export/{export}/{gen}.
# The `{name}/` directory matches the other backends.
clanDir: rel_dir: fileName:
clanDir + "/secrets/clan-vars/${rel_dir}/${fileName}/${fileName}.age"
