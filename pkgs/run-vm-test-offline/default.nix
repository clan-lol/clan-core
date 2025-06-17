{
  writeShellApplication,
  util-linux,
  coreutils,
}:

writeShellApplication {
  name = "run-vm-test-offline";
  runtimeInputs = [
    util-linux
    coreutils
  ]; # nix is inherited from the environment
  text = ''
    set -euo pipefail

    if [ $# -eq 0 ]; then
      echo "Error: Test name required"
      echo "Usage: nix run .#run-offline-test -- <test-name>"
      echo "Example: nix run .#run-offline-test -- installation"
      exit 1
    fi

    TEST_NAME="$1"

    echo "Building $TEST_NAME test driver..."
    SYSTEM=$(nix eval --impure --raw --expr 'builtins.currentSystem')
    nix build ".#checks.$SYSTEM.$TEST_NAME.driver"

    echo "Running $TEST_NAME test in offline environment..."
    # We use unshare here with root to avoid usernamespace issues originating from bubblewrap
    currentUser="$(whoami)"
    sudo unshare --net -- bash -c "
      ip link set lo up
      runuser -u $(printf "%q" "$currentUser") ./result/bin/nixos-test-driver
    "
  '';
  meta.description = "Run interactivly NixOS VM tests in an sandbox without network access";
}
