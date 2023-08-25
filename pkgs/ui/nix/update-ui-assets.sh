# shellcheck shell=bash

# GITEA_TOKEN
if [[ -z "${GITEA_TOKEN:-}" ]]; then
  echo "GITEA_TOKEN is not set"
  exit 1
fi

sha=$(git rev-parse HEAD)
PROJECT_DIR=$(git rev-parse --show-toplevel)
tmpdir=$(mktemp -d)
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT
nix build '.#ui' --out-link "$tmpdir/result"
tar --transform 's,^\.,assets,' -czvf "$tmpdir/assets.tar.gz" -C "$tmpdir"/result/lib/node_modules/*/out .
url="https://git.clan.lol/api/packages/clan/generic/ui/$sha/assets.tar.gz?token=$GITEA_TOKEN"
curl --upload-file "$tmpdir/assets.tar.gz" -X PUT "$url"
hash=$(nix-prefetch-url --unpack "$url")
cat > "$PROJECT_DIR/pkgs/ui/nix/ui-assets.nix" <<EOF
{ fetchzip }:
fetchzip {
  url = "$url";
  sha256 = "$hash";
}
EOF
