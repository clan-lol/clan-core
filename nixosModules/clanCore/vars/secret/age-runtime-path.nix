# Runtime path of an uploaded age-encrypted vars secret (external store).
#
# {secretLocation}/vars/{rel_dir}/{name}/{name}.age
#
# populate_dir in age.py uploads to this layout; age.nix decrypts from it.
# Pinned by ../eval-tests/age-source-path.nix.
secretLocation: rel_dir: fileName:
"${secretLocation}/vars/${rel_dir}/${fileName}/${fileName}.age"
