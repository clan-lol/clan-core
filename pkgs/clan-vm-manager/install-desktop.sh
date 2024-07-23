#!/usr/bin/env bash


if ! command -v xdg-mime &> /dev/null; then
  echo "Warning: 'xdg-mime' is not available. The desktop file cannot be installed."
fi

ALREADY_INSTALLED=$(nix profile list --json |  jq 'has("elements") and (.elements | has("clan-vm-manager"))')

if [ "$ALREADY_INSTALLED" = "true" ]; then
  echo "Upgrading installed clan-vm-manager"
  nix profile upgrade clan-vm-manager
else
  nix profile install .#clan-vm-manager
fi


# install desktop file
set -eou pipefail
DESKTOP_FILE_NAME=org.clan.vm-manager.desktop

xdg-mime default "$DESKTOP_FILE_NAME"  x-scheme-handler/clan
