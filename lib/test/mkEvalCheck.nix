/**
  Create a nix-unit eval check derivation with a descriptive name and
  a failure hint showing how to re-run the individual test.

  All eval checks should use this helper so we get consistent naming
  and error messages.

  Arguments:
    pkgs: nixpkgs package set
    name: the eval check name (will be prefixed with "evalCheck-" in legacyPackages)
    system: the system string (e.g. "x86_64-linux")
    flakeAttr: the full "--flake <src>#legacyPackages.<system>.<attr>" argument to nix-unit
    inputOverrides: input override flags from clanLib.flake-inputs.getOverrides
*/
{
  pkgs,
  name,
  system,
  flakeAttr,
  inputOverrides,
}:
pkgs.runCommand "evalCheck-${name}" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
  export HOME="$(realpath .)"
  trap 'if [ $? -ne 0 ]; then echo -e "\n\033[1;31mEval check failed.\033[0m To re-run this test:\n  nix build .#legacyPackages.${system}.evalCheck-${name}\n"; fi' EXIT

  nix-unit --eval-store "$HOME" \
    --extra-experimental-features flakes \
    --show-trace \
    ${inputOverrides} \
    --flake ${flakeAttr}

  touch $out
''
