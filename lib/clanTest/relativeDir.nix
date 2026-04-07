# Extract the relative path of a test directory from a nix store source path.
#
# When a downstream flake sets `directory = ./.;` in a test, it resolves to
# a nix store path like `/nix/store/<hash>-source/path/to/test`.
# We cannot use `removePrefix "${self}/"` because `self` is clan-core's outPath
# which has a different store hash than the downstream flake.
# Instead, we strip the `/nix/store/<hash>-<name>` prefix using a regex.
{ lib }:
let
  inherit (lib) removePrefix;
in
selfOutPath: dirStr:
let
  matched = builtins.match "${builtins.storeDir}/[^/]+(.*)" dirStr;
in
if matched != null then
  removePrefix "/" (builtins.head matched)
else
  # Fallback for non-store paths (e.g. local development with --impure)
  removePrefix "${selfOutPath}/" dirStr
