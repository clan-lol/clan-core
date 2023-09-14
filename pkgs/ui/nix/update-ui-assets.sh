# shellcheck shell=bash
set -xeuo pipefail

# GITEA_TOKEN
if [[ -z "${GITEA_TOKEN:-}" ]]; then
  echo "GITEA_TOKEN is not set"
  exit 1
fi

DEPS=$(nix shell --inputs-from '.#' "nixpkgs#gnutar" "nixpkgs#curl" "nixpkgs#gzip" -c bash -c "echo \$PATH")
export PATH=$PATH:$DEPS


PROJECT_DIR=$(git rev-parse --show-toplevel)
tmpdir=$(mktemp -d)
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT

nix build '.#ui' --out-link "$tmpdir/result"

tar --transform 's,^\.,assets,' -czvf "$tmpdir/assets.tar.gz" -C "$tmpdir"/result/lib/node_modules/*/out .
NAR_HASH=$(nix-prefetch-url --unpack file://<(cat "$tmpdir/assets.tar.gz"))


url="https://git.clan.lol/api/packages/clan/generic/ui/$NAR_HASH/assets.tar.gz"
curl -v --upload-file "$tmpdir/assets.tar.gz" -X PUT "$url?token=$GITEA_TOKEN"

TEST_URL=$(nix-prefetch-url --unpack "$url")
if [[ $TEST_URL != "$NAR_HASH" ]]; then
  echo "Prefetch failed. Expected $NAR_HASH, got $TEST_URL"
  exit 1
fi


cat > "$PROJECT_DIR/pkgs/ui/nix/ui-assets.nix" <<EOF
{ fetchzip }:
fetchzip {
  url = "$url";
  sha256 = "$NAR_HASH";
}
EOF


