#!/usr/bin/env bash

CLAN=$(nix build .#clan-app --print-out-paths)

if ! command -v xdg-mime &> /dev/null; then
  echo "Warning: 'xdg-mime' is not available. The desktop file cannot be installed."
fi

# install desktop file
set -eou pipefail
DESKTOP_FILE_NAME=org.clan.app.desktop
DESKTOP_DST=~/.local/share/applications/"$DESKTOP_FILE_NAME"
DESKTOP_SRC="$CLAN/share/applications/$DESKTOP_FILE_NAME"
UI_BIN="$CLAN/bin/clan-app"

cp -f "$DESKTOP_SRC" "$DESKTOP_DST"
sleep 2
sed -i "s|Exec=.*clan-app|Exec=$UI_BIN|" "$DESKTOP_DST"
xdg-mime default "$DESKTOP_FILE_NAME"  x-scheme-handler/clan
echo "==== Validating desktop file installation   ===="
set -x
desktop-file-validate "$DESKTOP_DST"
set +xeou pipefail
