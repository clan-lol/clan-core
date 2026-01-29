{
  pkgs,
}:
let
  # Get the nix package scope to access the patching mechanism
  nixScope = pkgs.nixVersions.nixComponents_2_31;

  # Apply our patch to the nix source
  patchedScope = nixScope.appendPatches [
    # Warn instead of error on chmod failure for overlay filesystems
    # This allows nix copy to work in container tests where the store
    # is mounted as an overlay with a read-only lower layer.
    # Upstream PR: TODO
    ./chmod-overlay-warning.patch
  ];
in
patchedScope.nix-everything
