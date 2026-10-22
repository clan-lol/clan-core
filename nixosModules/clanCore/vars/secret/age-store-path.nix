# Store path of an age-encrypted vars secret for the internal store, or null
# when the flake has no such file.
#
# The file is copied on its own. `clanDir` is usually the string form of the
# flake source, and a string below it keeps the whole source as context. A
# reference into that source would change with every commit to the clan,
# whatever the commit touched.
{ lib }:
let
  encryptedSourcePath = import ./age-source-path.nix;
in
clanDir: rel_dir: fileName:
let
  sourcePath = encryptedSourcePath clanDir rel_dir fileName;
in
if builtins.pathExists sourcePath then
  "${builtins.path {
    path = sourcePath;
    name = lib.strings.sanitizeDerivationName (baseNameOf sourcePath);
  }}"
else
  null
