{ lib }:
let
  computeRelativeDir = import ./relativeDir.nix { inherit lib; };
  clanCoreSelf = "/nix/store/aaaa-clan-core-source";
in
{
  # Same flake: clan-core's own test directory
  test_same_flake = {
    expr = computeRelativeDir clanCoreSelf "${clanCoreSelf}/clanServices/foo/tests/vm";
    expected = "clanServices/foo/tests/vm";
  };

  # Downstream flake: different store hash than clan-core
  test_downstream_flake = {
    expr = computeRelativeDir clanCoreSelf "/nix/store/bbbb-downstream-source/clanServices/bar/tests/vm";
    expected = "clanServices/bar/tests/vm";
  };

  # Flake root: directory is the store path itself (no subdirectory)
  test_flake_root = {
    expr = computeRelativeDir clanCoreSelf "/nix/store/cccc-some-source";
    expected = "";
  };

  # Non-store path fallback: local path matching self (e.g. --impure)
  test_local_fallback = {
    expr = computeRelativeDir "/home/user/project" "/home/user/project/tests/vm";
    expected = "tests/vm";
  };
}
